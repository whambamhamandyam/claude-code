'use client'

import { motion } from 'framer-motion'

export function VinylSpinner({ size = 120, label }: { size?: number; label?: string }) {
  return (
    <div className="flex flex-col items-center gap-4">
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        animate={{ rotate: 360 }}
        transition={{ duration: 2.5, repeat: Infinity, ease: 'linear' }}
        aria-hidden="true"
      >
        {/* Outer record body */}
        <circle cx="60" cy="60" r="58" fill="#1A0F0A" stroke="#2C1810" strokeWidth="2" />
        {/* Groove rings */}
        {[48, 42, 36, 30].map((r) => (
          <circle
            key={r}
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke="#3D2518"
            strokeWidth="1.2"
            opacity="0.8"
          />
        ))}
        {/* Label */}
        <circle cx="60" cy="60" r="19" fill="#D4813A" />
        {/* Center hole */}
        <circle cx="60" cy="60" r="3.5" fill="#1A0F0A" />
      </motion.svg>
      {label && (
        <p className="text-vinyl-cream/60 font-body text-sm tracking-widest uppercase animate-pulse">
          {label}
        </p>
      )}
    </div>
  )
}
