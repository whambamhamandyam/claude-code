export const runtime = 'nodejs'

import { NextRequest, NextResponse } from 'next/server'
import { searchYouTube } from '@/lib/youtube'

export async function GET(req: NextRequest) {
  const artist = req.nextUrl.searchParams.get('artist')
  const track = req.nextUrl.searchParams.get('track')

  if (!artist || !track) {
    return NextResponse.json({ error: 'artist and track required' }, { status: 400 })
  }

  const result = await searchYouTube(artist, track)
  return NextResponse.json(result, {
    headers: {
      'Cache-Control': 'public, max-age=86400',
    },
  })
}
