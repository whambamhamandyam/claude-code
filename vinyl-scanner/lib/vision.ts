import 'server-only'
import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

export async function extractAlbumFromImage(
  base64Image: string
): Promise<{ artist: string; album: string } | null> {
  try {
    const message = await client.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 256,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: 'image/jpeg',
                data: base64Image,
              },
            },
            {
              type: 'text',
              text: `This is a photograph of a vinyl record sleeve. Extract the artist name and album title from it.
Return ONLY valid JSON in this exact format, with no extra text or markdown:
{"artist": "Artist Name", "album": "Album Title"}
If you cannot determine a value with confidence, use null for that field.`,
            },
          ],
        },
      ],
    })

    const text = (message.content[0] as { type: 'text'; text: string }).text.trim()

    // Handle potential markdown code fences
    const jsonStr = text.replace(/^```(?:json)?\n?/i, '').replace(/\n?```$/i, '').trim()
    try {
      return JSON.parse(jsonStr)
    } catch {
      const match = text.match(/\{[\s\S]+?\}/)
      return match ? JSON.parse(match[0]) : null
    }
  } catch {
    return null
  }
}
