'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

interface CameraViewProps {
  onBarcodeDetected: (barcode: string) => void
  onPhotoCapture: (base64: string) => void
  onClose: () => void
}

export function CameraView({ onBarcodeDetected, onPhotoCapture, onClose }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const readerRef = useRef<unknown>(null)
  const detectedRef = useRef(false)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [showPhotoHint, setShowPhotoHint] = useState(false)

  useEffect(() => {
    let active = true
    let hintTimer: ReturnType<typeof setTimeout>

    async function startCamera() {
      try {
        let stream: MediaStream
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
            audio: false,
          })
        } catch {
          // Fallback for desktop (no environment camera)
          stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        }

        if (!active) { stream.getTracks().forEach((t) => t.stop()); return }
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }

        // Dynamic import to avoid SSR crash
        const { BrowserMultiFormatReader } = await import('@zxing/browser')
        const reader = new BrowserMultiFormatReader()
        readerRef.current = reader

        reader.decodeFromVideoElement(videoRef.current!, (result, err) => {
          if (result && active && !detectedRef.current) {
            detectedRef.current = true
            onBarcodeDetected(result.getText())
          }
          // Suppress expected "not found" errors from continuous scanning
          void err
        })

        // Show photo hint after 3s of no barcode
        hintTimer = setTimeout(() => {
          if (active && !detectedRef.current) setShowPhotoHint(true)
        }, 3000)
      } catch (err) {
        const error = err as Error
        if (error.name === 'NotAllowedError') {
          setCameraError('Camera access denied. Please allow camera access in your browser settings.')
        } else if (error.name === 'NotFoundError') {
          setCameraError('No camera found on this device.')
        } else {
          setCameraError('Could not access camera. Please try again.')
        }
      }
    }

    startCamera()

    return () => {
      active = false
      clearTimeout(hintTimer)
      if (readerRef.current) {
        try { (readerRef.current as { reset?: () => void }).reset?.() } catch { /* ignore */ }
      }
      streamRef.current?.getTracks().forEach((t) => t.stop())
    }
  }, [onBarcodeDetected])

  const capturePhoto = useCallback(async () => {
    if (!videoRef.current) return
    const video = videoRef.current
    const canvas = document.createElement('canvas')
    // Resize to max 1024px to limit payload size for vision API
    const maxDim = 1024
    const scale = Math.min(maxDim / video.videoWidth, maxDim / video.videoHeight, 1)
    canvas.width = Math.round(video.videoWidth * scale)
    canvas.height = Math.round(video.videoHeight * scale)
    canvas.getContext('2d')!.drawImage(video, 0, 0, canvas.width, canvas.height)
    const base64 = canvas.toDataURL('image/jpeg', 0.85).split(',')[1]
    onPhotoCapture(base64)
  }, [onPhotoCapture])

  if (cameraError) {
    return (
      <div className="fixed inset-0 z-50 bg-vinyl-charcoal flex flex-col items-center justify-center p-8 gap-6">
        <svg width="64" height="64" viewBox="0 0 64 64" className="text-vinyl-amber" aria-hidden="true">
          <circle cx="32" cy="32" r="30" fill="none" stroke="currentColor" strokeWidth="3" />
          <line x1="32" y1="18" x2="32" y2="36" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <circle cx="32" cy="46" r="2.5" fill="currentColor" />
        </svg>
        <p className="text-vinyl-cream text-center font-body">{cameraError}</p>
        <button
          onClick={onClose}
          className="px-6 py-3 rounded-full bg-vinyl-amber text-vinyl-charcoal font-display font-semibold"
        >
          Go Back
        </button>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col">
      {/* Video stream */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />

      {/* Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-between py-16 pointer-events-none">
        {/* Top label */}
        <div className="bg-vinyl-charcoal/70 rounded-full px-5 py-2">
          <p className="text-vinyl-cream font-body text-sm tracking-wider">
            Point at barcode or sleeve
          </p>
        </div>

        {/* Barcode targeting frame */}
        <div className="flex flex-col items-center gap-6">
          <div
            className="border-2 border-vinyl-amber rounded-xl"
            style={{ width: 280, height: 100 }}
          >
            {/* Corner accents */}
            <div className="relative w-full h-full">
              {[
                'top-0 left-0 border-t-2 border-l-2',
                'top-0 right-0 border-t-2 border-r-2',
                'bottom-0 left-0 border-b-2 border-l-2',
                'bottom-0 right-0 border-b-2 border-r-2',
              ].map((cls, i) => (
                <div
                  key={i}
                  className={`absolute w-5 h-5 border-vinyl-gold ${cls}`}
                  style={{ margin: -1 }}
                />
              ))}
            </div>
          </div>

          {showPhotoHint && (
            <p className="text-vinyl-cream/80 font-body text-sm animate-pulse">
              No barcode found — try capturing a photo
            </p>
          )}
        </div>

        {/* Bottom placeholder for pointer-events */}
        <div />
      </div>

      {/* Controls */}
      <div
        className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-8 pb-safe"
        style={{ paddingBottom: 'calc(2rem + env(safe-area-inset-bottom, 0px))' }}
      >
        <button
          onClick={onClose}
          className="w-12 h-12 rounded-full bg-vinyl-brown/80 flex items-center justify-center pointer-events-auto"
          aria-label="Cancel"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <line x1="4" y1="4" x2="16" y2="16" stroke="#F5E6C8" strokeWidth="2" strokeLinecap="round" />
            <line x1="16" y1="4" x2="4" y2="16" stroke="#F5E6C8" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>

        <button
          onClick={capturePhoto}
          className="w-20 h-20 rounded-full border-4 border-vinyl-cream bg-vinyl-cream/20 flex items-center justify-center pointer-events-auto active:scale-95 transition-transform"
          aria-label="Capture photo"
        >
          <div className="w-14 h-14 rounded-full bg-vinyl-cream" />
        </button>

        <div className="w-12" />
      </div>
    </div>
  )
}
