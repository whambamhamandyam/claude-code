import 'server-only'
import type { YouTubeResult } from './types'

export async function searchYouTube(
  artist: string,
  trackName: string
): Promise<YouTubeResult | null> {
  try {
    const q = encodeURIComponent(`${artist} ${trackName}`)
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${q}&type=video&maxResults=1&key=${process.env.YOUTUBE_API_KEY}`
    const res = await fetch(url, { next: { revalidate: 86400 } })
    if (!res.ok) return null
    const data = await res.json()
    const videoId = data.items?.[0]?.id?.videoId
    if (!videoId) return null
    return {
      videoId,
      url: `https://www.youtube.com/watch?v=${videoId}`,
    }
  } catch {
    return null
  }
}
