#!/usr/bin/env bash
# Cloudflare build (see wrangler.jsonc). Every branch, including ticket
# branches, gets a preview served from the domain root, so the site is rebuilt
# without the GitHub Pages /bm-industrial-solutions prefix and the public files
# are copied into dist/.
#
# Cloudflare build command: `bash _build/pages.sh`.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 _build/build.py --base "" --site-url https://www.bmindustrialsolutionsllc.com
python3 _build/check.py --base ""

rm -rf dist
mkdir dist
cp -R index.html 404.html robots.txt sitemap.xml favicon.ico \
  assets about contact services service-areas dist/

# Previews only: keep them out of search results. Remove this when the
# Cloudflare Worker starts serving the real domain.
printf '/*\n  X-Robots-Tag: noindex\n' > dist/_headers
