# BM Industrial Solutions — website

Static HTML site for [BM Industrial Solutions](https://www.bmindustrialsolutionsllc.com/),
served by GitHub Pages. No frameworks, no runtime dependencies, no build step on
the server — the HTML in this repo is exactly what visitors receive.

## Layout

```
index.html                 Home
about/                     About
contact/                   Contact + quote form
services/                  Services hub
  air-compressor-services/   ├─ air-compressor-repair/
                             ├─ air-compressor-installation/
                             └─ air-compressor-maintenance/
  hydraulics-services/       ├─ hydraulics-repair/
                             └─ hydraulics-maintenance/
  mechanical-contracting/
  process-piping/
  preventive-maintenance/
service-areas/             Service areas hub + 6 city pages
404.html                   Not-found page
assets/                    css, js, images (committed, ready to serve)
_build/                    The generator — see below
```

Every URL matches the paths on the current live site, so nothing breaks when
DNS is pointed here. `services/preventive-maintenance/` is the one addition —
it was marketed on the old homepage but had no page.

## Rebuilding

Pages are generated from Python templates. After editing content, run:

```bash
python3 _build/build.py          # regenerate all 22 pages
python3 _build/check.py          # verify links, assets and metadata
```

Requires Python 3.9+. No packages needed for the page build.

| File | What it holds |
| --- | --- |
| `_build/content.py` | **All copy and data.** Services, service areas, FAQs, company details. Edit here. |
| `_build/render.py` | HTML components — nav, cards, sections, structured data, page shell. |
| `_build/build.py` | Composes components into pages and writes them to disk. |
| `_build/check.py` | Post-build validation. Exits non-zero on a broken link. |
| `_build/images.py` | Photo pipeline. Needs `_inbox/` and Pillow; only re-run when adding photos. |

### Changing text

Almost everything lives in `_build/content.py`. To change a service
description, a FAQ answer or the phone number, edit it there and re-run the
build. Nothing needs to be edited in the generated HTML — it is overwritten.

### Adding photos

1. Drop originals into `_inbox/photos/`.
2. Add an entry to the `PHOTOS` dict in `_build/images.py`.
3. `pip3 install Pillow && python3 _build/images.py`
4. Reference the new slug from `_build/content.py`.

EXIF rotation is applied automatically — 25 of the original 49 photos needed it.

## Deployment

GitHub Pages serves this repo directly. `.nojekyll` stops Pages from running
the files through Jekyll.

### Project URL (current)

The site is built for `https://ridgelinedm.github.io/bm-industrial-solutions`,
which serves from a subpath, so internal links carry a `/bm-industrial-solutions`
prefix. That is the default:

```bash
python3 _build/build.py
```

### Custom domain (when DNS moves)

Serving from the root of `bmindustrialsolutionsllc.com` means no prefix:

```bash
python3 _build/build.py --base "" --site-url https://www.bmindustrialsolutionsllc.com
python3 _build/check.py --base ""
echo "www.bmindustrialsolutionsllc.com" > CNAME
```

Then point DNS at GitHub Pages and enable HTTPS in the repo settings. The
`--site-url` flag also updates canonicals, the sitemap and structured data, so
do not skip it.

## Two things still to wire up

1. **The contact form endpoint.** `contact/` posts to Formspree, but the form
   ID is a placeholder. Create a form at [formspree.io](https://formspree.io),
   then replace `YOUR_FORM_ID` in the `data-endpoint` and `action` attributes
   (set in `_build/build.py`, `page_contact()`). Until that is done the form
   degrades gracefully: `assets/js/site.js` detects the placeholder and opens a
   pre-filled email instead, so it is never a dead end.

2. **Testimonials.** `TESTIMONIALS` in `_build/content.py` is an empty list, and
   the testimonials section does not render while it is empty. Add real,
   attributed reviews as `(quote, name, role, stars)` tuples and they will
   appear on the homepage. They were deliberately left blank rather than
   invented.

## Design notes

Brand colours were sampled from the logo artwork: red `#CE171E`, ink `#231F20`,
grey `#686868`. Type is Archivo (display) over Inter (body).

The layout follows the reference site's language rather than just its spacing:

- **Bento grid** (`.bento`) — the service lines render as an asymmetric grid of
  solid colour-blocked panels at mixed widths, with photography bleeding to the
  card edge. The reference uses lavender/yellow/pink; we use the only palette
  the brand owns — ink, red, and two industrial neutrals (`#efece6` bone,
  `#e4e8ea` mist) — plus a full-bleed photo surface. Layout is configured in
  `BENTO_LAYOUT` in `_build/build.py`.
- **Ring button** (`.btn--ring`) — a filled pill inside an offset outline with a
  gap of background colour between, driven by `--ring-gap` and `--ring-line`.
- **Split section heads** — any left-aligned heading with supporting copy
  automatically renders as two columns, heading left and lead right.
- **Accented headline words** — `<em>` inside a heading prints in brand red, and
  inverts on red and ink grounds so it never disappears into its background.
- **Bare icon grids** (`.featurelist`) and muted wordmark walls instead of the
  boxed-icon card and chip-row patterns they replaced.

Accent colours are deliberately limited to the brand palette. If you add a new
surface, check the `em` accent still has contrast against it.

Accessibility and performance basics are in place: one `<h1>` per page, alt text
on every image, visible focus rings, `prefers-reduced-motion` honoured, skip
link, responsive `<picture>` sources at four widths with JPEG fallbacks, and no
external requests other than Google Fonts.
