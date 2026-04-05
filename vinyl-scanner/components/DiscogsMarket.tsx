'use client'

import { useEffect, useState } from 'react'
import type { DiscogsMarketData } from '@/lib/types'

// Condition label abbreviation map
const CONDITION_ABBR: Record<string, string> = {
  'Mint (M)': 'M',
  'Near Mint (NM or M-)': 'NM',
  'Very Good Plus (VG+)': 'VG+',
  'Very Good (VG)': 'VG',
  'Good Plus (G+)': 'G+',
  'Good (G)': 'G',
  'Fair (F)': 'F',
  'Poor (P)': 'P',
}

function formatPrice(price: number | null) {
  if (price == null) return 'N/A'
  return `$${price.toFixed(2)}`
}

interface DiscogsMarketProps {
  releaseId: string
  artist: string
  album: string
}

export function DiscogsMarket({ releaseId, artist, album }: DiscogsMarketProps) {
  const [data, setData] = useState<DiscogsMarketData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch(`/api/discogs?releaseId=${encodeURIComponent(releaseId)}`)
      .then((r) => {
        if (!r.ok) throw new Error()
        return r.json()
      })
      .then((d: DiscogsMarketData) => { setData(d); setLoading(false) })
      .catch(() => { setError(true); setLoading(false) })
  }, [releaseId])

  const conditions = data
    ? Object.entries(data.conditionBreakdown).sort((a, b) => b[1] - a[1])
    : []

  return (
    <section className="mt-6 mb-24" aria-label="Secondary market">
      <h2 className="text-vinyl-cream/60 font-display text-xs tracking-widest uppercase mb-3">
        Market Value
      </h2>

      <div
        className="rounded-2xl p-4 space-y-4"
        style={{
          background: 'linear-gradient(135deg, rgba(44,24,16,0.8), rgba(26,15,10,0.9))',
          border: '1px solid rgba(196,154,60,0.2)',
        }}
      >
        {loading ? (
          <div className="animate-pulse space-y-3">
            <div className="flex gap-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex-1 h-14 bg-vinyl-brown/60 rounded-xl" />
              ))}
            </div>
            <div className="h-8 bg-vinyl-brown/40 rounded-lg" />
          </div>
        ) : error ? (
          <div className="text-center py-2">
            <p className="text-vinyl-cream/40 font-body text-sm mb-2">
              Market data unavailable
            </p>
            <a
              href={`https://www.discogs.com/search?q=${encodeURIComponent(`${artist} ${album}`)}&type=release`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-vinyl-amber font-body text-sm underline"
            >
              Search on Discogs →
            </a>
          </div>
        ) : data ? (
          <>
            {/* Price range */}
            <div className="flex gap-2">
              {[
                { label: 'Low', value: data.lowestPrice },
                { label: 'Median', value: data.medianPrice },
                { label: 'High', value: data.highestPrice },
              ].map(({ label, value }) => (
                <div
                  key={label}
                  className="flex-1 rounded-xl p-3 text-center"
                  style={{ background: 'rgba(26,15,10,0.6)', border: '1px solid rgba(212,129,58,0.1)' }}
                >
                  <p className="text-vinyl-cream/50 font-body text-xs uppercase tracking-wider mb-1">
                    {label}
                  </p>
                  <p className="text-vinyl-gold font-display text-lg font-bold">
                    {formatPrice(value)}
                  </p>
                </div>
              ))}
            </div>

            {/* Active listings */}
            <div className="flex items-center justify-between">
              <span className="text-vinyl-cream/60 font-body text-sm">
                {data.activeListings} listings for sale
              </span>
            </div>

            {/* Condition breakdown */}
            {conditions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {conditions.slice(0, 6).map(([cond, count]) => (
                  <div
                    key={cond}
                    className="flex items-center gap-1.5 rounded-full px-3 py-1"
                    style={{ background: 'rgba(212,129,58,0.1)', border: '1px solid rgba(212,129,58,0.2)' }}
                  >
                    <span className="text-vinyl-amber font-body text-xs font-semibold">
                      {CONDITION_ABBR[cond] ?? cond}
                    </span>
                    <span className="text-vinyl-cream/50 font-body text-xs">{count}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Buy link */}
            <a
              href={data.buyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl font-display font-semibold text-sm transition-opacity hover:opacity-90 active:scale-98"
              style={{
                background: 'linear-gradient(135deg, #D4813A, #C46A22)',
                color: '#1A0F0A',
              }}
            >
              View on Discogs
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                <path
                  d="M3 7H11M8 4L11 7L8 10"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </a>
          </>
        ) : null}
      </div>
    </section>
  )
}
