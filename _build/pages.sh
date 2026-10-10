#!/usr/bin/env bash
# Cloudflare Pages build. Every branch, including ticket branches, gets a
# preview at <branch>.<project>.pages.dev, served from the domain root, so the
# site is rebuilt without the GitHub Pages /bm-industrial-solutions prefix and
# the public files are copied into dist/ (the Pages output directory).
#
# Cloudflare settings: build command `bash _build/pages.sh`, output `dist`.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 _build/build.py --base "" --site-url https://www.bmindustrialsolutionsllc.com
python3 _build/check.py --base ""

rm -rf dist
mkdir dist
cp -R index.html 404.html robots.txt sitemap.xml favicon.ico \
  assets about contact services service-areas dist/
