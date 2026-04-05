export interface IdentifyResult {
  artist: string
  album: string
  spotifyAlbumId: string | null
  discogsReleaseId: string | null
  coverArtUrl: string | null
  identificationMethod: 'barcode' | 'vision'
}

export interface Track {
  trackNumber: number
  trackName: string
  durationMs: number
  previewUrl: string | null
  spotifyTrackId: string
  spotifyTrackUrl: string
}

export interface DiscogsMarketData {
  lowestPrice: number | null
  medianPrice: number | null
  highestPrice: number | null
  activeListings: number
  conditionBreakdown: Record<string, number>
  buyUrl: string
}

export interface YouTubeResult {
  videoId: string
  url: string
}

export interface RecentScan {
  albumId: string
  artist: string
  album: string
  coverArtUrl: string | null
  scannedAt: number
}
