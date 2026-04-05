'use client'

export default function OfflinePage() {
  return (
    <main
      className="min-h-screen flex flex-col items-center justify-center gap-6 px-6 text-center"
      style={{ background: 'radial-gradient(ellipse at 50% 30%, #2C1810 0%, #1A0F0A 65%)' }}
    >
      {/* Vinyl with cracked groove */}
      <svg width="120" height="120" viewBox="0 0 120 120" aria-hidden="true">
        <circle cx="60" cy="60" r="58" fill="#1A0F0A" stroke="#2C1810" strokeWidth="2" />
        {[48, 42, 36, 30].map((r) => (
          <circle key={r} cx="60" cy="60" r={r} fill="none" stroke="#2C1810" strokeWidth="1.2" opacity="0.8" />
        ))}
        <circle cx="60" cy="60" r="19" fill="#D4813A" />
        <circle cx="60" cy="60" r="3.5" fill="#1A0F0A" />
        {/* Signal-off indicator */}
        <line x1="80" y1="40" x2="40" y2="80" stroke="#D4813A" strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
      </svg>

      <div>
        <h1 className="font-display text-3xl font-bold text-vinyl-cream mb-2">No Signal</h1>
        <p className="text-vinyl-cream/60 font-body text-sm max-w-xs">
          You&apos;re offline. Connect to the internet to scan records and check market prices.
        </p>
      </div>

      <button
        onClick={() => window.location.reload()}
        className="px-6 py-3 rounded-full font-display font-semibold text-vinyl-charcoal"
        style={{ background: 'linear-gradient(135deg, #D4813A, #C46A22)' }}
      >
        Try Again
      </button>
    </main>
  )
}
