'use client'

import { createContext, useContext, useRef, useState, useCallback } from 'react'
import type { Track } from './types'

interface AudioContextValue {
  currentTrack: Track | null
  isPlaying: boolean
  progress: number
  play: (track: Track) => void
  pause: () => void
  togglePlay: (track: Track) => void
}

const AudioCtx = createContext<AudioContextValue | null>(null)

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)

  const getAudio = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio()
      audioRef.current.ontimeupdate = () => {
        if (audioRef.current) {
          setProgress(audioRef.current.currentTime / (audioRef.current.duration || 1))
        }
      }
      audioRef.current.onended = () => {
        setIsPlaying(false)
        setProgress(0)
      }
    }
    return audioRef.current
  }, [])

  const play = useCallback(
    (track: Track) => {
      if (!track.previewUrl) return
      const audio = getAudio()
      // Change track only if different
      if (currentTrack?.spotifyTrackId !== track.spotifyTrackId) {
        audio.src = track.previewUrl
        setCurrentTrack(track)
        setProgress(0)
      }
      audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
    },
    [currentTrack, getAudio]
  )

  const pause = useCallback(() => {
    audioRef.current?.pause()
    setIsPlaying(false)
  }, [])

  const togglePlay = useCallback(
    (track: Track) => {
      if (currentTrack?.spotifyTrackId === track.spotifyTrackId && isPlaying) {
        pause()
      } else {
        play(track)
      }
    },
    [currentTrack, isPlaying, play, pause]
  )

  return (
    <AudioCtx.Provider value={{ currentTrack, isPlaying, progress, play, pause, togglePlay }}>
      {children}
    </AudioCtx.Provider>
  )
}

export function useAudio() {
  const ctx = useContext(AudioCtx)
  if (!ctx) throw new Error('useAudio must be used within AudioProvider')
  return ctx
}
