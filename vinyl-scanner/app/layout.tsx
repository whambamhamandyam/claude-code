import type { Metadata, Viewport } from 'next'
import './globals.css'
import { AudioProvider } from '@/lib/AudioContext'
import { MiniPlayer } from '@/components/MiniPlayer'

export const metadata: Metadata = {
  title: 'CrateDigger',
  description: 'Scan vinyl records for instant track lists and market prices',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'CrateDigger',
  },
  icons: {
    apple: '/icons/icon-192.png',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#2C1810',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased bg-vinyl-charcoal">
        <AudioProvider>
          {children}
          <MiniPlayer />
        </AudioProvider>
      </body>
    </html>
  )
}
