import 'server-only'
import type { Track } from './types'

const SPOTIFY_API = 'https://api.spotify.com/v1'
const SPOTIFY_AUTH = 'https://accounts.spotify.com/api/token'

let cachedToken: { access_token: string; expires_at: number } | null = null

async function getAccessToken(): Promise<string> {
  if (cachedToken && Date.now() < cachedToken.expires_at - 5000) {
    return cachedToken.access_token
  }
  const creds = Buffer.from(
    `${process.env.SPOTIFY_CLIENT_ID}:${process.env.SPOTIFY_CLIENT_SECRET}`
  ).toString('base64')

  const res = await fetch(SPOTIFY_AUTH, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${creds}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
    cache: 'no-store',
  })

  if (!res.ok) throw new Error(`Spotify auth failed: ${res.status}`)
  const data = await res.json()
  cachedToken = {
    access_token: data.access_token,
    expires_at: Date.now() + data.expires_in * 1000,
  }
  return cachedToken.access_token
}

export async function searchSpotifyAlbum(artist: string, album: string) {
  const token = await getAccessToken()
  const q = encodeURIComponent(`album:${album} artist:${artist}`)
  const res = await fetch(`${SPOTIFY_API}/search?q=${q}&type=album&limit=1`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { revalidate: 3600 },
  })
  if (!res.ok) return null
  const data = await res.json()
  return data.albums?.items?.[0] ?? null
}

export async function getSpotifyAlbumTracks(albumId: string): Promise<Track[]> {
  const token = await getAccessToken()
  const res = await fetch(`${SPOTIFY_API}/albums/${albumId}/tracks?limit=50`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { revalidate: 3600 },
  })
  if (!res.ok) return []
  const data = await res.json()

  return (data.items ?? []).map((item: Record<string, unknown>, idx: number) => ({
    trackNumber: (item.track_number as number) ?? idx + 1,
    trackName: item.name as string,
    durationMs: item.duration_ms as number,
    previewUrl: (item.preview_url as string | null) ?? null,
    spotifyTrackId: item.id as string,
    spotifyTrackUrl: `https://open.spotify.com/track/${item.id}`,
  }))
}
