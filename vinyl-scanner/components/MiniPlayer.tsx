'use client'

import { useAudio } from '@/lib/AudioContext'
import { motion, AnimatePresence } from 'framer-motion'

export function MiniPlayer() {
  const { currentTrack, isPlaying, progress, pause, play } = useAudio()

  return (
    <AnimatePresence>
      {currentTrack && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 28, stiffness: 300 }}
          className="fixed left-4 right-4 z-40 rounded-2xl overflow-hidden"
          style={{
            bottom: 'calc(1rem + env(safe-area-inset-bottom, 0px))',
            background: 'linear-gradient(135deg, #3D2518, #2C1810)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px rgba(212,129,58,0.2)',
          }}
        >
          {/* Progress bar */}
          <div className="h-0.5 w-full bg-vinyl-brown/60">
            <motion.div
              className="h-full bg-vinyl-amber"
              style={{ width: `${progress * 100}%` }}
            />
          </div>

          <div className="flex items-center gap-3 px-4 py-3">
            {/* Mini vinyl icon */}
            <div className="w-9 h-9 rounded-full bg-vinyl-charcoal flex items-center justify-center shrink-0">
              <svg
                width="28"
                height="28"
                viewBox="0 0 28 28"
                aria-hidden="true"
                className={isPlaying ? 'animate-[spinVinyl_3s_linear_infinite]' : ''}
              >
                <circle cx="14" cy="14" r="13" fill="#1A0F0A" />
                {[10, 8, 6].map((r) => (
                  <circle key={r} cx="14" cy="14" r={r} fill="none" stroke="#2C1810" strokeWidth="1" />
                ))}
                <circle cx="14" cy="14" r="4" fill="#D4813A" />
                <circle cx="14" cy="14" r="1.5" fill="#1A0F0A" />
              </svg>
            </div>

            {/* Track info */}
            <div className="flex-1 min-w-0">
              <p className="text-vinyl-cream font-body text-sm truncate">{currentTrack.trackName}</p>
              <p className="text-vinyl-amber/60 font-body text-xs">30s preview</p>
            </div>

            {/* Play/Pause */}
            <button
              onClick={() => (isPlaying ? pause() : play(currentTrack))}
              className="w-11 h-11 rounded-full bg-vinyl-amber flex items-center justify-center shrink-0 active:scale-95 transition-transform"
              aria-label={isPlaying ? 'Pause' : 'Resume'}
            >
              {isPlaying ? (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <rect x="3" y="2" width="3.5" height="12" rx="1" fill="#1A0F0A" />
                  <rect x="9.5" y="2" width="3.5" height="12" rx="1" fill="#1A0F0A" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M4.5 2.5L13 8L4.5 13.5V2.5Z" fill="#1A0F0A" />
                </svg>
              )}
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
