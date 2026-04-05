'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'
import Image from 'next/image'
import { ScanButton } from '@/components/ScanButton'
import { VinylSpinner } from '@/components/VinylSpinner'
import type { IdentifyResult, RecentScan } from '@/lib/types'

// Dynamic import: @zxing/browser must never be SSR'd
const CameraView = dynamic(
  () => import('@/components/CameraView').then((m) => ({ default: m.CameraView })),
  { ssr: false }
)

function useRecentScans() {
  const getScans = (): RecentScan[] => {
    if (typeof window === 'undefined') return []
    try { return JSON.parse(localStorage.getItem('recentScans') ?? '[]') } catch { return [] }
  }
  const addScan = (scan: RecentScan) => {
    const scans = getScans()
    localStorage.setItem('recentScans', JSON.stringify([scan, ...scans].slice(0, 3)))
  }
  return { getScans, addScan }
}

export default function HomePage() {
  const router = useRouter()
  const { getScans, addScan } = useRecentScans()
  const [cameraOpen, setCameraOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recentScans] = useState<RecentScan[]>(() =>
    typeof window !== 'undefined' ? getScans() : []
  )

  const identify = useCallback(
    async (payload: { barcode?: string; imageBase64?: string }) => {
      setLoading(true)
      setCameraOpen(false)
      setError(null)
      try {
        const res = await fetch('/api/identify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.error ?? 'Could not identify record')
        }
        const data: IdentifyResult = await res.json()
        const albumId = data.spotifyAlbumId ?? (data.discogsReleaseId ? `discogs-${data.discogsReleaseId}` : 'unknown')

        // Persist for results page
        sessionStorage.setItem(`album-${albumId}`, JSON.stringify(data))

        // Save recent scan
        addScan({
          albumId,
          artist: data.artist,
          album: data.album,
          coverArtUrl: data.coverArtUrl,
          scannedAt: Date.now(),
        })

        // Navigate with key params in URL as fallback
        const params = new URLSearchParams()
        if (data.spotifyAlbumId) params.set('s', data.spotifyAlbumId)
        if (data.discogsReleaseId) params.set('d', data.discogsReleaseId)
        router.push(`/results/${encodeURIComponent(albumId)}?${params}`)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Something went wrong. Please try again.')
      } finally {
        setLoading(false)
      }
    },
    [router, addScan]
  )

  return (
    <main
      className="min-h-screen flex flex-col items-center justify-between relative overflow-hidden px-6"
      style={{ background: 'radial-gradient(ellipse at 50% 30%, #2C1810 0%, #1A0F0A 65%)' }}
    >
      {/* Vinyl groove texture */}
      <div
        className="absolute inset-0 opacity-[0.035] pointer-events-none"
        style={{
          backgroundImage:
            'repeating-radial-gradient(circle at 50% 50%, transparent 0, transparent 18px, rgba(212,129,58,0.5) 19px, transparent 20px)',
        }}
      />

      {/* Header */}
      <header className="pt-16 text-center z-10">
        <h1 className="font-display text-4xl font-bold text-vinyl-cream tracking-tight">
          CrateDigger
        </h1>
        <p className="text-vinyl-amber/80 font-body text-sm mt-2 tracking-widest uppercase">
          Scan · Sample · Score
        </p>
      </header>

      {/* Scan button + feedback */}
      <div className="flex flex-col items-center gap-6 z-10">
        {loading ? (
          <VinylSpinner size={140} label="Identifying…" />
        ) : (
          <ScanButton onPress={() => setCameraOpen(true)} isScanning={cameraOpen} />
        )}

        <p className="text-vinyl-cream/40 font-body text-sm text-center max-w-xs">
          Tap to scan a barcode or photograph the sleeve
        </p>

        {error && (
          <div className="bg-red-900/30 border border-red-500/30 rounded-xl px-4 py-3 max-w-xs text-center">
            <p className="text-red-300 font-body text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Recent scans */}
      <div className="w-full max-w-sm pb-12 z-10">
        {recentScans.length > 0 && (
          <div className="space-y-2">
            <p className="text-vinyl-cream/40 font-body text-xs tracking-widest uppercase text-center mb-3">
              Recent scans
            </p>
            {recentScans.map((scan) => (
              <button
                key={scan.scannedAt}
                onClick={() => router.push(`/results/${encodeURIComponent(scan.albumId)}`)}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-vinyl-brown/40 border border-vinyl-amber/10 text-left active:scale-[0.98] transition-transform"
              >
                {scan.coverArtUrl ? (
                  <Image
                    src={scan.coverArtUrl}
                    alt=""
                    width={40}
                    height={40}
                    className="w-10 h-10 rounded-lg object-cover shrink-0"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-lg bg-vinyl-charcoal shrink-0 flex items-center justify-center">
                    <span className="text-vinyl-amber/60 text-xs">♪</span>
                  </div>
                )}
                <div className="min-w-0">
                  <p className="text-vinyl-cream font-body text-sm truncate">{scan.album}</p>
                  <p className="text-vinyl-amber/60 font-body text-xs truncate">{scan.artist}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Camera */}
      {cameraOpen && (
        <CameraView
          onBarcodeDetected={(code) => identify({ barcode: code })}
          onPhotoCapture={(base64) => identify({ imageBase64: base64 })}
          onClose={() => setCameraOpen(false)}
        />
      )}
    </main>
  )
}
