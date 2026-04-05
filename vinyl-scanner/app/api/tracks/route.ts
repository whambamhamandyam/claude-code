export const runtime = 'nodejs'

import { NextRequest, NextResponse } from 'next/server'
import { getSpotifyAlbumTracks } from '@/lib/spotify'

export async function GET(req: NextRequest) {
  const albumId = req.nextUrl.searchParams.get('albumId')
  if (!albumId) {
    return NextResponse.json({ error: 'albumId required' }, { status: 400 })
  }

  const tracks = await getSpotifyAlbumTracks(albumId)
  return NextResponse.json(tracks, {
    headers: {
      'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
    },
  })
}
