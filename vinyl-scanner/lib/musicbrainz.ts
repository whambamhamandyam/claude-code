import 'server-only'

const MB_BASE = 'https://musicbrainz.org/ws/2'
const MB_HEADERS = {
  'User-Agent': 'CrateDigger/1.0 (cratedigger@example.com)',
  Accept: 'application/json',
}

export interface MBRelease {
  id: string
  title: string
  artist: string
  date?: string
}

export async function lookupByBarcode(barcode: string): Promise<MBRelease | null> {
  try {
    const url = `${MB_BASE}/release?query=barcode:${encodeURIComponent(barcode)}&fmt=json&limit=1`
    const res = await fetch(url, { headers: MB_HEADERS, next: { revalidate: 86400 } })
    if (!res.ok) return null
    const data = await res.json()
    const release = data.releases?.[0]
    if (!release) return null
    return {
      id: release.id,
      title: release.title,
      artist: release['artist-credit']?.[0]?.artist?.name ?? release['artist-credit']?.[0]?.name ?? '',
      date: release.date,
    }
  } catch {
    return null
  }
}
