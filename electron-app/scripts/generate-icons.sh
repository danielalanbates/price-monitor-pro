#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ASSETS_DIR="${PROJECT_ROOT}/assets"
ICON_SVG="${ASSETS_DIR}/icon.svg"

cd "${PROJECT_ROOT}"

echo "🎨 Generating app icons from SVG..."

# Create PNG at 512x512
magick -background none "${ICON_SVG}" -resize 512x512 "${ASSETS_DIR}/icon.png"
echo "✅ Created icon.png (512x512)"

# Create iconset directory for macOS
ICONSET_DIR="${ASSETS_DIR}/icon.iconset"
mkdir -p "${ICONSET_DIR}"

# Generate all required sizes for macOS .icns
magick -background none "${ICON_SVG}" -resize 16x16 "${ICONSET_DIR}/icon_16x16.png"
magick -background none "${ICON_SVG}" -resize 32x32 "${ICONSET_DIR}/icon_16x16@2x.png"
magick -background none "${ICON_SVG}" -resize 32x32 "${ICONSET_DIR}/icon_32x32.png"
magick -background none "${ICON_SVG}" -resize 64x64 "${ICONSET_DIR}/icon_32x32@2x.png"
magick -background none "${ICON_SVG}" -resize 128x128 "${ICONSET_DIR}/icon_128x128.png"
magick -background none "${ICON_SVG}" -resize 256x256 "${ICONSET_DIR}/icon_128x128@2x.png"
magick -background none "${ICON_SVG}" -resize 256x256 "${ICONSET_DIR}/icon_256x256.png"
magick -background none "${ICON_SVG}" -resize 512x512 "${ICONSET_DIR}/icon_256x256@2x.png"
magick -background none "${ICON_SVG}" -resize 512x512 "${ICONSET_DIR}/icon_512x512.png"
magick -background none "${ICON_SVG}" -resize 1024x1024 "${ICONSET_DIR}/icon_512x512@2x.png"

echo "✅ Generated all iconset sizes"

# Convert iconset to .icns
iconutil -c icns "${ICONSET_DIR}" -o "${ASSETS_DIR}/icon.icns"
echo "✅ Created icon.icns"

# Clean up iconset directory
rm -rf "${ICONSET_DIR}"

echo "🎉 Icon generation complete!"
