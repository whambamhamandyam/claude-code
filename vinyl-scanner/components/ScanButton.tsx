'use client'

import { motion } from 'framer-motion'

interface ScanButtonProps {
  onPress: () => void
  isScanning?: boolean
}

export function ScanButton({ onPress, isScanning = false }: ScanButtonProps) {
  return (
    <div className="relative flex items-center justify-center" style={{ width: 200, height: 200 }}>
      {/* Pulsing ripple rings */}
      {[0, 0.7, 1.4].map((delay) => (
        <motion.div
          key={delay}
          className="absolute rounded-full border border-vinyl-amber/30"
          style={{ width: 200, height: 200 }}
          animate={{ scale: [1, 1.7], opacity: [0.5, 0] }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay,
            ease: 'easeOut',
          }}
        />
      ))}

      {/* Button */}
      <motion.button
        className="relative z-10 w-36 h-36 rounded-full flex flex-col items-center justify-center gap-1 shadow-2xl focus:outline-none"
        style={{
          background: 'radial-gradient(circle at 35% 35%, #E8923F, #C46A22)',
          boxShadow: '0 0 40px rgba(212,129,58,0.4), inset 0 1px 0 rgba(255,255,255,0.15)',
        }}
        whileTap={{ scale: 0.93 }}
        onTap={isScanning ? undefined : onPress}
        onClick={isScanning ? undefined : onPress}
        disabled={isScanning}
        aria-label="Scan a vinyl record"
      >
        {/* Vinyl record icon */}
        <svg width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">
          <circle cx="22" cy="22" r="20" fill="#1A0F0A" />
          {[16, 13, 10].map((r) => (
            <circle key={r} cx="22" cy="22" r={r} fill="none" stroke="#2C1810" strokeWidth="1" />
          ))}
          <circle cx="22" cy="22" r="6" fill="#D4813A" />
          <circle cx="22" cy="22" r="2" fill="#1A0F0A" />
        </svg>
        <span className="text-vinyl-charcoal font-display font-bold text-xs tracking-widest uppercase">
          Scan
        </span>
      </motion.button>
    </div>
  )
}
