'use client'

import { TrackCard } from './TrackCard'
import type { Track } from '@/lib/types'

function TrackSkeleton() {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-vinyl-charcoal/40 border border-vinyl-amber/5 animate-pulse">
      <div className="w-5 h-4 bg-vinyl-brown/60 rounded" />
      <div className="flex-1 space-y-2">
        <div className="h-3.5 bg-vinyl-brown/60 rounded w-3/4" />
        <div className="h-2.5 bg-vinyl-brown/40 rounded w-1/4" />
      </div>
      <div className="w-11 h-11 rounded-full bg-vinyl-brown/60 shrink-0" />
      <div className="w-11 h-11 rounded-full bg-vinyl-brown/60 shrink-0" />
      <div className="w-11 h-11 rounded-full bg-vinyl-brown/60 shrink-0" />
    </div>
  )
}

interface TrackListProps {
  tracks: Track[]
  loading: boolean
  artist: string
}

export function TrackList({ tracks, loading, artist }: TrackListProps) {
  return (
    <section className="space-y-2" aria-label="Track list">
      <h2 className="text-vinyl-cream/60 font-display text-xs tracking-widest uppercase mb-3">
        Tracklist
      </h2>

      {loading ? (
        <>
          {Array.from({ length: 8 }).map((_, i) => (
            <TrackSkeleton key={i} />
          ))}
        </>
      ) : tracks.length === 0 ? (
        <p className="text-vinyl-cream/40 font-body text-sm text-center py-6">
          No tracks found on Spotify
        </p>
      ) : (
        tracks.map((track) => (
          <TrackCard key={track.spotifyTrackId} track={track} artist={artist} />
        ))
      )}
    </section>
  )
}
