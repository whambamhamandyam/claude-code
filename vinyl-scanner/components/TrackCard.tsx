'use client'

import { useState } from 'react'
import { useAudio } from '@/lib/AudioContext'
import type { Track } from '@/lib/types'

function formatDuration(ms: number) {
  const s = Math.round(ms / 1000)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

interface TrackCardProps {
  track: Track
  artist: string
}

export function TrackCard({ track, artist }: TrackCardProps) {
  const { currentTrack, isPlaying, togglePlay } = useAudio()
  const isCurrentTrack = currentTrack?.spotifyTrackId === track.spotifyTrackId
  const isThisPlaying = isCurrentTrack && isPlaying

  const [ytUrl, setYtUrl] = useState<string | null>(null)
  const [ytLoading, setYtLoading] = useState(false)

  async function handleYouTube() {
    if (ytUrl) {
      window.open(ytUrl, '_blank', 'noopener,noreferrer')
      return
    }
    setYtLoading(true)
    try {
      const res = await fetch(
        `/api/youtube?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(track.trackName)}`
      )
      const data = await res.json()
      if (data?.url) {
        setYtUrl(data.url)
        window.open(data.url, '_blank', 'noopener,noreferrer')
      }
    } finally {
      setYtLoading(false)
    }
  }

  return (
    <div
      className={`flex items-center gap-3 p-3 rounded-xl transition-colors ${
        isCurrentTrack
          ? 'bg-vinyl-amber/15 border border-vinyl-amber/30'
          : 'bg-vinyl-charcoal/40 border border-vinyl-amber/5 hover:bg-vinyl-brown/50'
      }`}
    >
      {/* Track number */}
      <span className="text-vinyl-gold/60 font-display text-sm w-5 text-right shrink-0">
        {isThisPlaying ? (
          <span className="text-vinyl-amber">▶</span>
        ) : (
          track.trackNumber
        )}
      </span>

      {/* Track info */}
      <div className="flex-1 min-w-0">
        <p
          className={`font-body text-sm truncate ${
            isCurrentTrack ? 'text-vinyl-amber' : 'text-vinyl-cream'
          }`}
        >
          {track.trackName}
        </p>
        <p className="text-vinyl-cream/40 font-body text-xs">
          {formatDuration(track.durationMs)}
          {!track.previewUrl && (
            <span className="ml-2 text-vinyl-cream/25">No preview</span>
          )}
        </p>
      </div>

      {/* Play preview */}
      <button
        onClick={() => togglePlay(track)}
        disabled={!track.previewUrl}
        className={`w-11 h-11 rounded-full flex items-center justify-center transition-colors shrink-0 ${
          track.previewUrl
            ? 'bg-vinyl-amber/20 hover:bg-vinyl-amber/40 active:scale-95'
            : 'opacity-25 cursor-not-allowed'
        }`}
        aria-label={isThisPlaying ? 'Pause preview' : 'Play 30s preview'}
        title={track.previewUrl ? undefined : 'No preview available'}
      >
        {isThisPlaying ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <rect x="3" y="2" width="3.5" height="12" rx="1" fill="#D4813A" />
            <rect x="9.5" y="2" width="3.5" height="12" rx="1" fill="#D4813A" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M4 2.5L13 8L4 13.5V2.5Z" fill={track.previewUrl ? '#D4813A' : '#F5E6C8'} />
          </svg>
        )}
      </button>

      {/* Spotify */}
      <a
        href={track.spotifyTrackUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="w-11 h-11 rounded-full flex items-center justify-center bg-[#1DB954]/15 hover:bg-[#1DB954]/30 transition-colors shrink-0 active:scale-95"
        aria-label={`Open ${track.trackName} in Spotify`}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="12" fill="#1DB954" />
          <path
            d="M7 16.5c3.5-1.5 8-1.2 10.5 1"
            stroke="white"
            strokeWidth="1.8"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M6.5 13c4-1.8 9-1.4 12 1.2"
            stroke="white"
            strokeWidth="1.8"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M6 9.5c4.5-2 10-1.5 13.5 1.5"
            stroke="white"
            strokeWidth="1.8"
            strokeLinecap="round"
            fill="none"
          />
        </svg>
      </a>

      {/* YouTube */}
      <button
        onClick={handleYouTube}
        disabled={ytLoading}
        className="w-11 h-11 rounded-full flex items-center justify-center bg-[#FF0000]/15 hover:bg-[#FF0000]/30 transition-colors shrink-0 active:scale-95 disabled:opacity-50"
        aria-label={`Open ${track.trackName} on YouTube`}
      >
        {ytLoading ? (
          <div className="w-3 h-3 rounded-full border-2 border-red-400 border-t-transparent animate-spin" />
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
            <rect x="0" y="0" width="24" height="24" rx="5" fill="#FF0000" />
            <path d="M10 8.5L16 12L10 15.5V8.5Z" fill="white" />
          </svg>
        )}
      </button>
    </div>
  )
}
