#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
APP_NAME="Price Monitor Pro.app"
DEST_PATH="/Applications/${APP_NAME}"

cd "${PROJECT_ROOT}"

echo "🚀 Building latest macOS bundle..."
npm run build:mac

echo "🔍 Selecting architecture-specific build..."
ARCH="$(uname -m)"
if [[ "${ARCH}" == "arm64" && -d "${DIST_DIR}/mac-arm64/${APP_NAME}" ]]; then
    SOURCE_PATH="${DIST_DIR}/mac-arm64/${APP_NAME}"
else
    SOURCE_PATH="${DIST_DIR}/mac/${APP_NAME}"
fi

if [[ ! -d "${SOURCE_PATH}" ]]; then
    echo "❌ Could not find built app at ${SOURCE_PATH}" >&2
    exit 1
fi

echo "🧹 Removing existing copy at ${DEST_PATH} (requires permissions)..."
if [[ -d "${DEST_PATH}" ]]; then
    rm -rf "${DEST_PATH}"
fi

echo "📦 Copying updated app to /Applications..."
ditto "${SOURCE_PATH}" "${DEST_PATH}"

echo "✅ Installed ${APP_NAME} to ${DEST_PATH}"
