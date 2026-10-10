# BM Industrial Solutions website

Static HTML site for [BM Industrial Solutions](https://www.bmindustrialsolutionsllc.com/),
served by GitHub Pages. No frameworks, no runtime dependencies, no build step on
the server. The HTML in this repo is exactly what visitors receive.

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
_build/                    The generator, see below
```

Every URL matches the paths on the current live site, so nothing breaks when
DNS is pointed here. `services/preventive-maintenance/` is the one addition:
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
| `_build/render.py` | HTML components: nav, cards, sections, structured data, page shell. |
| `_build/build.py` | Composes components into pages and writes them to disk. |
| `_build/check.py` | Post-build validation. Exits non-zero on a broken link. |
| `_build/images.py` | Photo pipeline. Needs `_inbox/` and Pillow; only re-run when adding photos. |

### Changing text

Almost everything lives in `_build/content.py`. To change a service
description, a FAQ answer or the phone number, edit it there and re-run the
build. Nothing needs to be edited in the generated HTML; it is overwritten.

**Two house rules for copy.** Both exist because they are the fingerprints of
machine-written text, and this site should not read that way.

1. **No em dashes.** Use a colon when a list follows, parentheses for a genuine
   aside, a full stop when the clause can stand alone, otherwise a comma.
2. **No "X, not Y" antithesis.** Say the thing directly instead of defining it
   against its opposite. "You get a technician, not a ticket number" becomes
   "a technician picks up the phone." The same applies to "not just X but Y",
   "instead of", and "rather than" when it is used for rhetorical contrast
   rather than a real comparison. "Measured in hours rather than days" is a
   genuine comparison and is fine; "diagnose the cause rather than repeating
   the repair" was rhetoric and got rewritten.

Verbatim customer reviews are exempt from both. They are quotes from named
people and are rendered as written.

### Adding photos

1. Drop originals into `_inbox/photos/`.
2. Add an entry to the `PHOTOS` dict in `_build/images.py`.
3. `pip3 install Pillow && python3 _build/images.py`
4. Reference the new slug from `_build/content.py`.

EXIF rotation is applied automatically. 25 of the original 49 photos needed it.

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

## Ticket automation

ClickUp tickets become PRs that Claude writes, and go live when you approve
them in ClickUp. The Cloudflare Worker in `~/Projects/ridgeline-ticket-worker`
turns ClickUp status changes into GitHub `repository_dispatch` events.

| ClickUp status | What happens |
| --- | --- |
| **ready for build** | `ticket-to-pr.yml` reads the ticket, Claude edits the source on branch `CU-<task id>`, the workflow rebuilds, runs `check.py`, refuses changes to `.github/`, `_inbox/` or `CNAME`, opens a PR, comments the PR and preview links on the ticket, moves it to **internal review** and assigns the reviewer |
| **internal review** | You check the preview. Comment `@claude <what to change>` on the PR to revise (`claude-revise.yml`) |
| **deploy** | `ticket-deploy.yml` squash-merges the PR, which publishes it, and sets the ticket to **complete**. If it cannot, it comments why and moves the ticket back to internal review |

Merging the PR on GitHub yourself also works: `ticket-merged.yml` then closes
the ticket. Both ticket workflows can be run by hand from the Actions tab with
a task ID. Claude's standing instructions for the repo are in `CLAUDE.md`.

| Setting | Kind | Value |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` | secret | Claude credentials (one of the two) |
| `CLICKUP_API_TOKEN` | secret | ClickUp personal token (`pk_...`) |
| `CLICKUP_REVIEWER_ID` | variable | ClickUp user assigned for review (`174105881`, Zach) |
| `CF_PAGES_PROJECT` | variable | Cloudflare Pages project name, for preview links |
| `CLICKUP_REVIEW_STATUS` | variable | Defaults to `internal review` |
| `CLICKUP_DONE_STATUS` | variable | Defaults to `complete` |

The repo allows Actions to open PRs, and `main` requires a PR (no approvals).

## Two things still to wire up

1. **The contact form endpoint.** `contact/` posts to Formspree, but the form
   ID is a placeholder. Create a form at [formspree.io](https://formspree.io),
   then replace `YOUR_FORM_ID` in the `data-endpoint` and `action` attributes
   (set in `_build/build.py`, `page_contact()`). Until that is done the form
   degrades gracefully: `assets/js/site.js` detects the placeholder and opens a
   pre-filled email instead, so it is never a dead end.

2. **The "Read them on Google" link.** `google_reviews_url` in
   `_build/content.py` currently points at a Google *search* for the business,
   not the review profile itself. Replace it with the real profile link (Google
   Business Profile gives you one under "Get more reviews"). The location ID in
   the export is not the same as the place ID, so it cannot be derived.

## Reviews

Reviews are imported from a Google Business Profile export. They are never
hand-written: if `_build/reviews.json` is missing or empty, the reviews section
does not render at all.

```bash
# 1. Drop the export into _inbox/reviews/ (or leave it loose in _inbox/
#    as long as the filename starts with "review"). .json or .csv both work.
python3 _build/reviews.py     # 2. parse it into _build/reviews.json
python3 _build/build.py       # 3. rebuild the pages
```

`_build/reviews.py` understands the Business Profile API shape (nested
`reviewer.displayName`, word ratings like `"FIVE"`, ISO `createTime`), a flat
JSON array, or a CSV with any sensible header naming. It de-duplicates across
files, drops star-only ratings that have no comment to display, and sorts
longest-first so the masonry fills evenly.

Two counts come out of it: `count` is reviews with written text (what gets
rendered as cards) and `total` is every rating on the profile (what the
headline score is calculated from), so the "N reviews" figure matches Google
rather than the number of cards on screen.

The raw exports stay in `_inbox/`, which is git-ignored — they carry your
account and location IDs. Only the parsed `reviews.json` is committed.

Review text is rendered verbatim. The importer strips two things that are
decoration rather than content: a leading row of star emoji some people type,
and a trailing rule like `————`. Punctuation *inside* a review is left exactly
as written, because these are attributed quotes from named people.

Set `ABBREVIATE_SURNAMES = True` at the top of `_build/reviews.py` to render
"Jane D." instead of full names.

**No `aggregateRating` schema.** The star rating is displayed but deliberately
not marked up in structured data. Google disallows self-serving review markup
on `LocalBusiness`, and adding it risks a manual action against the whole
site's rich results. The reviews still work as social proof for humans.

## Design notes

Brand colours were sampled from the logo artwork: red `#CE171E`, ink `#231F20`,
grey `#686868`. Type is Archivo (display) over Inter (body).

The layout follows the reference site's language rather than just its spacing:

- **Bento grid** (`.bento`). The service lines render as an asymmetric grid of
  solid colour-blocked panels at mixed widths, with photography bleeding to the
  card edge. The reference uses lavender/yellow/pink; we use the only palette
  the brand owns: ink, red, and two industrial neutrals (`#efece6` bone,
  `#e4e8ea` mist), plus a full-bleed photo surface. Layout is configured in
  `BENTO_LAYOUT` in `_build/build.py`.
- **Ring button** (`.btn--ring`). A filled pill inside an offset outline with a
  gap of background colour between, driven by `--ring-gap` and `--ring-line`.
- **Split section heads.** Any left-aligned heading with supporting copy
  automatically renders as two columns, heading left and lead right.
- **Accented headline words.** `<em>` inside a heading prints in brand red, and
  inverts on red and ink grounds so it never disappears into its background.
- **Bare icon grids** (`.featurelist`) and muted wordmark walls instead of the
  boxed-icon card and chip-row patterns they replaced.

Accent colours are deliberately limited to the brand palette. If you add a new
surface, check the `em` accent still has contrast against it.

Accessibility and performance basics are in place: one `<h1>` per page, alt text
on every image, visible focus rings, `prefers-reduced-motion` honoured, skip
link, responsive `<picture>` sources at four widths with JPEG fallbacks, and no
external requests other than Google Fonts.
