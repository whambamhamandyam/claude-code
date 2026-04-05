'use client'

import { Suspense, useEffect, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { AlbumHeader } from '@/components/AlbumHeader'
import { TrackList } from '@/components/TrackList'
import { DiscogsMarket } from '@/components/DiscogsMarket'
import type { IdentifyResult, Track } from '@/lib/types'

function ResultsContent() {
  const { albumId } = useParams<{ albumId: string }>()
  const searchParams = useSearchParams()
  const router = useRouter()

  const [albumData, setAlbumData] = useState<IdentifyResult | null>(null)
  const [tracks, setTracks] = useState<Track[]>([])
  const [tracksLoading, setTracksLoading] = useState(true)

  // Restore identification result: sessionStorage first, URL params as fallback
  useEffect(() => {
    const decodedId = decodeURIComponent(albumId)
    const stored = sessionStorage.getItem(`album-${decodedId}`)
    if (stored) {
      setAlbumData(JSON.parse(stored))
      return
    }
    const spotifyId = searchParams.get('s')
    const discogsId = searchParams.get('d')
    if (spotifyId || discogsId) {
      setAlbumData({
        artist: '',
        album: '',
        spotifyAlbumId: spotifyId,
        discogsReleaseId: discogsId,
        coverArtUrl: null,
        identificationMethod: 'barcode',
      })
    }
  }, [albumId, searchParams])

  useEffect(() => {
    if (!albumData?.spotifyAlbumId) {
      setTracksLoading(false)
      return
    }
    setTracksLoading(true)
    fetch(`/api/tracks?albumId=${encodeURIComponent(albumData.spotifyAlbumId)}`)
      .then((r) => r.json())
      .then((data: Track[]) => {
        setTracks(data)
        setTracksLoading(false)
      })
      .catch(() => setTracksLoading(false))
  }, [albumData?.spotifyAlbumId])

  return (
    <div className="min-h-screen bg-vinyl-charcoal">
      <button
        onClick={() => router.push('/')}
        className="absolute top-4 left-4 z-10 w-10 h-10 rounded-full bg-vinyl-charcoal/70 flex items-center justify-center"
        aria-label="Back to scanner"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <path
            d="M11 4L6 9L11 14"
            stroke="#F5E6C8"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      <AlbumHeader albumData={albumData} />

      <motion.div
        initial={{ y: 60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', damping: 28, stiffness: 200, delay: 0.1 }}
        className="rounded-t-3xl px-4 pt-6"
        style={{ background: 'linear-gradient(180deg, #2C1810 0%, #1A0F0A 100%)' }}
      >
        <TrackList tracks={tracks} loading={tracksLoading} artist={albumData?.artist ?? ''} />

        {!tracksLoading && !albumData?.spotifyAlbumId && (
          <div className="text-center py-6">
            <p className="text-vinyl-cream/40 font-body text-sm">No Spotify match found.</p>
            <a
              href={`https://open.spotify.com/search/${encodeURIComponent(
                `${albumData?.artist ?? ''} ${albumData?.album ?? ''}`
              )}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-vinyl-amber font-body text-sm underline mt-1 inline-block"
            >
              Search Spotify manually →
            </a>
          </div>
        )}

        {albumData?.discogsReleaseId ? (
          <DiscogsMarket
            releaseId={albumData.discogsReleaseId}
            artist={albumData.artist}
            album={albumData.album}
          />
        ) : (
          !tracksLoading && (
            <div className="mt-6 mb-24 text-center">
              <p className="text-vinyl-cream/40 font-body text-sm mb-1">
                No Discogs listing found.
              </p>
              <a
                href={`https://www.discogs.com/search?q=${encodeURIComponent(
                  `${albumData?.artist ?? ''} ${albumData?.album ?? ''}`
                )}&type=release`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-vinyl-amber font-body text-sm underline"
              >
                Search Discogs manually →
              </a>
            </div>
          )
        )}
      </motion.div>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-vinyl-charcoal flex items-center justify-center">
          <div className="w-10 h-10 rounded-full border-2 border-vinyl-amber border-t-transparent animate-spin" />
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  )
}
