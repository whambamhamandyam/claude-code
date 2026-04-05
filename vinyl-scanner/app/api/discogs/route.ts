export const runtime = 'nodejs'

import { NextRequest, NextResponse } from 'next/server'
import { getMarketData } from '@/lib/discogs'

export async function GET(req: NextRequest) {
  const releaseId = req.nextUrl.searchParams.get('releaseId')
  if (!releaseId) {
    return NextResponse.json({ error: 'releaseId required' }, { status: 400 })
  }

  const data = await getMarketData(releaseId)
  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, max-age=900, stale-while-revalidate=3600',
    },
  })
}
