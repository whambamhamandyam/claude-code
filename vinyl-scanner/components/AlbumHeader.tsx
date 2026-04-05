'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import type { IdentifyResult } from '@/lib/types'

export function AlbumHeader({ albumData }: { albumData: IdentifyResult | null }) {
  if (!albumData) return null

  return (
    <div
      className="relative flex flex-col items-center pt-12 pb-8 px-6 gap-4"
      style={{
        background: 'radial-gradient(ellipse at top, #3D2518 0%, #1A0F0A 70%)',
      }}
    >
      {/* Vinyl groove texture overlay */}
      <div
        className="absolute inset-0 opacity-5 pointer-events-none"
        style={{
          backgroundImage:
            'repeating-radial-gradient(circle at 50% 50%, transparent 0px, transparent 8px, rgba(212,129,58,0.3) 9px, transparent 10px)',
        }}
      />

      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', damping: 20, stiffness: 200 }}
        className="relative"
      >
        {albumData.coverArtUrl ? (
          <div className="w-48 h-48 rounded-lg overflow-hidden shadow-2xl ring-2 ring-vinyl-amber/30">
            <Image
              src={albumData.coverArtUrl}
              alt={`${albumData.album} cover art`}
              width={192}
              height={192}
              className="object-cover w-full h-full"
            />
          </div>
        ) : (
          <div className="w-48 h-48 rounded-lg bg-vinyl-brown flex items-center justify-center shadow-2xl ring-2 ring-vinyl-amber/30">
            <svg width="72" height="72" viewBox="0 0 72 72" aria-hidden="true">
              <circle cx="36" cy="36" r="34" fill="#1A0F0A" />
              {[28, 22, 16].map((r) => (
                <circle key={r} cx="36" cy="36" r={r} fill="none" stroke="#2C1810" strokeWidth="1.5" />
              ))}
              <circle cx="36" cy="36" r="9" fill="#D4813A" />
              <circle cx="36" cy="36" r="3" fill="#1A0F0A" />
            </svg>
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.15 }}
        className="text-center"
      >
        <h1 className="text-vinyl-cream font-display text-2xl font-bold leading-tight">
          {albumData.album}
        </h1>
        <p className="text-vinyl-amber font-body text-base mt-1">{albumData.artist}</p>
      </motion.div>

      {albumData.identificationMethod === 'vision' && (
        <span className="text-vinyl-gold/70 font-body text-xs tracking-widest uppercase border border-vinyl-gold/30 rounded-full px-3 py-1">
          Identified by AI
        </span>
      )}
    </div>
  )
}
