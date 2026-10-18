#!/usr/bin/env bash
# Cloudflare build (see wrangler.jsonc). Every branch, including ticket
# branches, gets a preview served from the domain root. Astro builds the site
# into dist/, then check.py validates links, assets and metadata.
#
# Cloudflare build command: `bash _build/pages.sh`.
set -euo pipefail
cd "$(dirname "$0")/.."

npm ci --no-audit --no-fund
SITE_URL=https://www.bmindustrialsolutionsllc.com BASE_PATH="" npx astro build
python3 _build/check.py --root dist --base ""

# Previews only: keep them out of search results. Remove this when the
# Cloudflare Worker starts serving the real domain.
printf '/*\n  X-Robots-Tag: noindex\n' > dist/_headers
