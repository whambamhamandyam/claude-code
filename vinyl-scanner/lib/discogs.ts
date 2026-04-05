import 'server-only'
import type { DiscogsMarketData } from './types'

const BASE = 'https://api.discogs.com'
const headers = () => ({
  Authorization: `Discogs token=${process.env.DISCOGS_TOKEN}`,
  'User-Agent': 'CrateDigger/1.0',
})

export interface DiscogsRelease {
  id: number
  title: string
  thumb: string
  type: string
  master_id?: number
}

export async function searchDiscogs(params: {
  barcode?: string
  artist?: string
  releaseTitle?: string
}): Promise<DiscogsRelease | null> {
  try {
    const q = new URLSearchParams({ type: 'release' })
    if (params.barcode) q.set('barcode', params.barcode)
    if (params.artist) q.set('artist', params.artist)
    if (params.releaseTitle) q.set('release_title', params.releaseTitle)

    const res = await fetch(`${BASE}/database/search?${q}`, {
      headers: headers(),
      next: { revalidate: 3600 },
    })
    if (!res.ok) return null
    const data = await res.json()
    return data.results?.[0] ?? null
  } catch {
    return null
  }
}

export async function getMarketData(releaseId: string): Promise<DiscogsMarketData> {
  const buyUrl = `https://www.discogs.com/sell/list?release_id=${releaseId}`

  try {
    const [statsRes, listingsRes] = await Promise.all([
      fetch(`${BASE}/marketplace/stats/${releaseId}`, { headers: headers() }),
      fetch(`${BASE}/marketplace/listings?release_id=${releaseId}&per_page=100&sort=price&sort_order=asc`, {
        headers: headers(),
      }),
    ])

    const stats = statsRes.ok ? await statsRes.json() : null
    const listingsData = listingsRes.ok ? await listingsRes.json() : null

    // Aggregate condition breakdown
    const conditionBreakdown: Record<string, number> = {}
    const listings: Array<{ condition: string; price: { value: number } }> =
      listingsData?.listings ?? []

    const prices: number[] = []
    for (const listing of listings) {
      const cond = listing.condition
      conditionBreakdown[cond] = (conditionBreakdown[cond] ?? 0) + 1
      if (listing.price?.value) prices.push(listing.price.value)
    }

    const lowestPrice = stats?.lowest_price?.value ?? (prices[0] ?? null)
    const highestPrice = prices.length > 0 ? prices[prices.length - 1] : null
    const medianPrice =
      prices.length > 0 ? prices[Math.floor(prices.length / 2)] : null

    return {
      lowestPrice,
      medianPrice,
      highestPrice,
      activeListings: stats?.num_for_sale ?? listings.length,
      conditionBreakdown,
      buyUrl,
    }
  } catch {
    return {
      lowestPrice: null,
      medianPrice: null,
      highestPrice: null,
      activeListings: 0,
      conditionBreakdown: {},
      buyUrl,
    }
  }
}
