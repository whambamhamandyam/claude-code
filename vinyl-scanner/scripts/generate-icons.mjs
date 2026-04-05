/**
 * Generates SVG-based PWA icons as PNG using sharp.
 * Run: node scripts/generate-icons.mjs
 */
import sharp from 'sharp'
import { writeFileSync } from 'fs'

const svg = (size) => `
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${size * 0.1}" fill="#2C1810"/>
  <!-- Outer record -->
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.42}" fill="#1A0F0A"/>
  <!-- Groove rings -->
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.38}" fill="none" stroke="#2C1810" stroke-width="${size*0.012}"/>
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.32}" fill="none" stroke="#2C1810" stroke-width="${size*0.012}"/>
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.26}" fill="none" stroke="#2C1810" stroke-width="${size*0.012}"/>
  <!-- Label -->
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.15}" fill="#D4813A"/>
  <!-- Label text -->
  <text x="${size/2}" y="${size/2 + size*0.025}" text-anchor="middle" font-family="Georgia,serif" font-size="${size*0.065}" font-weight="bold" fill="#1A0F0A">CD</text>
  <!-- Center hole -->
  <circle cx="${size/2}" cy="${size/2}" r="${size*0.025}" fill="#1A0F0A"/>
</svg>`

for (const size of [192, 512]) {
  await sharp(Buffer.from(svg(size)))
    .png()
    .toFile(`public/icons/icon-${size}.png`)
  console.log(`Generated icon-${size}.png`)
}
