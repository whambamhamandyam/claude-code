export const runtime = 'nodejs'

import { NextRequest, NextResponse } from 'next/server'
import { lookupByBarcode } from '@/lib/musicbrainz'
import { extractAlbumFromImage } from '@/lib/vision'
import { searchDiscogs } from '@/lib/discogs'
import { searchSpotifyAlbum } from '@/lib/spotify'
import type { IdentifyResult } from '@/lib/types'

export async function POST(req: NextRequest) {
  const { barcode, imageBase64 } = await req.json()

  let artist: string | null = null
  let album: string | null = null
  let method: 'barcode' | 'vision' = 'barcode'

  // Barcode path
  if (barcode) {
    const mbResult = await lookupByBarcode(barcode)
    if (mbResult?.title && mbResult?.artist) {
      artist = mbResult.artist
      album = mbResult.title
    }
  }

  // Vision fallback
  if ((!artist || !album) && imageBase64) {
    method = 'vision'
    const visionResult = await extractAlbumFromImage(imageBase64)
    if (visionResult?.artist) artist = visionResult.artist
    if (visionResult?.album) album = visionResult.album
  }

  if (!artist || !album) {
    return NextResponse.json(
      { error: 'Could not identify record. Try capturing a clearer photo of the sleeve.' },
      { status: 422 }
    )
  }

  // Parallel Spotify + Discogs lookup — partial success is fine
  const [spotifyResult, discogsResult] = await Promise.allSettled([
    searchSpotifyAlbum(artist, album),
    searchDiscogs({ artist, releaseTitle: album }),
  ])

  const spotifyAlbum = spotifyResult.status === 'fulfilled' ? spotifyResult.value : null
  const discogsRelease = discogsResult.status === 'fulfilled' ? discogsResult.value : null

  const result: IdentifyResult = {
    artist,
    album,
    spotifyAlbumId: spotifyAlbum?.id ?? null,
    discogsReleaseId: discogsRelease?.id?.toString() ?? null,
    coverArtUrl:
      spotifyAlbum?.images?.[0]?.url ??
      (discogsRelease?.thumb && discogsRelease.thumb !== '' ? discogsRelease.thumb : null),
    identificationMethod: method,
  }

  return NextResponse.json(result)
}
