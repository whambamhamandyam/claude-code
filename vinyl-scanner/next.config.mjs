import withPWAInit from 'next-pwa'

const withPWA = withPWAInit({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\.spotify\.com\/.*/i,
      handler: 'NetworkFirst',
      options: { cacheName: 'spotify-api', expiration: { maxAgeSeconds: 300 } },
    },
    {
      urlPattern: /^https:\/\/i\.scdn\.co\/.*/i,
      handler: 'CacheFirst',
      options: { cacheName: 'spotify-images', expiration: { maxEntries: 50 } },
    },
    {
      urlPattern: /^https:\/\/.*\.discogs\.com\/.*/i,
      handler: 'CacheFirst',
      options: { cacheName: 'discogs-images', expiration: { maxEntries: 50 } },
    },
  ],
  fallbacks: {
    document: '/offline',
  },
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'i.scdn.co' },
      { protocol: 'https', hostname: '*.discogs.com' },
      { protocol: 'https', hostname: 'coverartarchive.org' },
      { protocol: 'https', hostname: 'i.discogs.com' },
    ],
  },
}

export default withPWA(nextConfig)
