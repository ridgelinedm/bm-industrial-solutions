#!/usr/bin/env python3
"""HTML component vocabulary for the BM Industrial Solutions site.

Everything here returns plain HTML strings. build.py composes pages out of
these; content.py holds the copy. No runtime dependencies; the output is
static HTML that GitHub Pages serves directly.
"""
import html
import json

from content import COMPANY, NAV, SERVICES, SERVICE_BY_SLUG, AREAS, BRANDS

SITE_URL = "https://ridgelinedm.github.io/bm-industrial-solutions"


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s), quote=True)


def url(path):
    """Absolute-from-root URL. `path` is '' for home, else 'services/foo'."""
    path = path.strip("/")
    return f"{BASE}/" if not path else f"{BASE}/{path}/"


# Set by build.py. Empty string for a user/org root site; "/repo" for a
# project site served from a subpath.
BASE = ""


def canonical(path):
    path = path.strip("/")
    return SITE_URL + "/" if not path else f"{SITE_URL}/{path}/"


# --------------------------------------------------------------------------
# Icons: Lucide-style 24px strokes, inlined so there is no icon-font request
# --------------------------------------------------------------------------
_ICON_PATHS = {
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    # Hydraulic cylinder: barrel, end caps, extended rod with clevis.
    "hydraulic": '<rect x="2" y="8" width="12" height="8" rx="1.5"/><path d="M14 12h5"/><circle cx="21" cy="12" r="2"/><path d="M5 8v8"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    # Process pipe run: flanged inlet, elbow, flanged outlet.
    "pipe": '<path d="M2 6h11a5 5 0 0 1 5 5v7"/><path d="M2 3.5v5"/><path d="M15 18h6"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M14 9h4l4 4v4a1 1 0 0 1-1 1h-1"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "bolt": '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/><path d="m6.08 9.5-3.5 1.6a1 1 0 0 0 0 1.81l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9a1 1 0 0 0 0-1.83l-3.5-1.59"/>',
    "settings": '<path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9c.14.63.71 1.09 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "star": '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    "list": '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    "quote": '<path d="M10 11H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v7a4 4 0 0 1-4 4"/><path d="M19 11h-4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v7a4 4 0 0 1-4 4"/>',
}


def icon(name, size=24, stroke=2, cls=""):
    d = _ICON_PATHS.get(name, "")
    c = f' class="{cls}"' if cls else ""
    return (
        f'<svg{c} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{d}</svg>'
    )


def star_icon(empty=False):
    cls = ' class="is-empty"' if empty else ""
    return (
        f'<svg{cls} width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>'
    )


def stars(rating, out_of=5):
    """Filled stars up to `rating`, greyed for the remainder."""
    rating = max(0, min(out_of, int(round(rating or 0))))
    marks = "".join(star_icon(empty=(i >= rating)) for i in range(out_of))
    return f'<span class="stars" role="img" aria-label="{rating} out of {out_of}">{marks}</span>'


# --------------------------------------------------------------------------
# Media
# --------------------------------------------------------------------------
def photo(slug, alt, sizes="100vw", cls="", loading="lazy", ratio=None, fetchpriority=None):
    """<picture> with a WebP srcset and a JPEG fallback."""
    widths = [400, 800, 1200, 1800]
    srcset = ", ".join(f"{BASE}/assets/img/photos/{slug}-{w}.webp {w}w" for w in widths)
    style = f' style="aspect-ratio:{ratio}"' if ratio else ""
    fp = f' fetchpriority="{fetchpriority}"' if fetchpriority else ""
    c = f' class="{cls}"' if cls else ""
    return (
        "<picture>"
        f'<source type="image/webp" srcset="{srcset}" sizes="{esc(sizes)}">'
        f'<img src="{BASE}/assets/img/photos/{slug}.jpg" alt="{esc(alt)}"'
        f'{c}{style} loading="{loading}" decoding="async"{fp} width="1200" height="900">'
        "</picture>"
    )


# --------------------------------------------------------------------------
# Chrome: top bar, nav, drawer, footer
# --------------------------------------------------------------------------
def topbar():
    return f"""<div class="topbar">
  <div class="container topbar__inner">
    <div class="topbar__items">
      <span class="topbar__item"><span class="pulse"></span><strong>24/7 Emergency Service</strong></span>
      <span class="topbar__item topbar__hide-sm">{icon('pin', 14, 2)} Serving South Carolina, Georgia &amp; North Carolina</span>
    </div>
    <div class="topbar__items">
      <a class="topbar__item" href="mailto:{COMPANY['email']}">{icon('mail', 14, 2)}<span class="topbar__hide-sm">{COMPANY['email']}</span></a>
      <a class="topbar__item" href="tel:{COMPANY['phone_href']}">{icon('phone', 14, 2)}<strong>{COMPANY['phone']}</strong></a>
    </div>
  </div>
</div>"""


def _nav_panel(items):
    rows = "".join(
        f'<a href="{url(i["path"])}"><strong>{esc(i["label"])}</strong><span>{esc(i["blurb"])}</span></a>'
        for i in items
    )
    return f'<div class="nav__panel">{rows}</div>'


def nav(active):
    links = []
    for item in NAV:
        is_active = active == item["key"] or active.startswith(item["key"] + ":")
        cls = "nav__link is-active" if is_active else "nav__link"
        cur = ' aria-current="page"' if active == item["key"] else ""
        if item.get("children"):
            links.append(
                f'<li class="nav__item"><a class="{cls}" href="{url(item["path"])}"{cur}>'
                f'{esc(item["label"])}{icon("chevron", 15, 2.4, "nav__caret")}</a>'
                f'{_nav_panel(item["children"])}</li>'
            )
        else:
            links.append(f'<li><a class="{cls}" href="{url(item["path"])}"{cur}>{esc(item["label"])}</a></li>')

    return f"""<header class="nav">
  <div class="container nav__inner">
    <a class="nav__logo" href="{url('')}" aria-label="{esc(COMPANY['name'])} home">
      <img src="{BASE}/assets/img/logo/logo-full-color.png" alt="{esc(COMPANY['name'])}" width="200" height="65">
    </a>
    <nav class="nav__nav" aria-label="Primary"><ul class="nav__menu">{''.join(links)}</ul></nav>
    <div class="nav__actions">
      <a class="nav__phone" href="tel:{COMPANY['phone_href']}">{icon('phone', 16, 2.2)}{COMPANY['phone']}</a>
      <a class="btn btn--primary btn--sm" href="{url('contact')}">Request a Quote</a>
      <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>"""


def drawer():
    blocks = []
    for item in NAV:
        if item.get("children"):
            subs = "".join(
                f'<a class="drawer__sub" href="{url(c["path"])}">{esc(c["label"])}</a>'
                for c in item["children"]
            )
            blocks.append(
                f'<div class="drawer__group"><a class="drawer__link" href="{url(item["path"])}">'
                f'{esc(item["label"])}</a>{subs}</div>'
            )
        else:
            blocks.append(f'<a class="drawer__link" href="{url(item["path"])}">{esc(item["label"])}</a>')

    return f"""<div class="drawer" id="drawer">
  <nav aria-label="Mobile">{''.join(blocks)}</nav>
  <div class="drawer__actions">
    <a class="btn btn--primary" href="{url('contact')}">Request a Quote</a>
    <a class="btn btn--outline" href="tel:{COMPANY['phone_href']}">{icon('phone', 17, 2.2)} {COMPANY['phone']}</a>
  </div>
</div>"""


def callbar():
    return f"""<div class="callbar">
  <a class="btn btn--outline btn--sm" href="{url('contact')}">Request a Quote</a>
  <a class="btn btn--primary btn--sm" href="tel:{COMPANY['phone_href']}">{icon('phone', 16, 2.2)} Call now</a>
</div>"""


def footer():
    svc_links = "".join(
        f'<li><a href="{url(s["path"])}">{esc(s["nav_title"])}</a></li>'
        for s in SERVICES if s.get("in_footer", True)
    )
    area_links = "".join(
        f'<li><a href="{url(a["path"])}">{esc(a["city"])}, {a["state"]}</a></li>' for a in AREAS
    )
    return f"""<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <div class="footer__logo">
          <img src="{BASE}/assets/img/logo/logo-full-reversed.png" alt="{esc(COMPANY['name'])}" width="210" height="68" loading="lazy">
        </div>
        <p class="footer__blurb">{esc(COMPANY['tagline'])} Owner-operated industrial service out of {COMPANY['city']}, {COMPANY['state']}. Compressed air, hydraulics, mechanical contracting and process piping under one number.</p>
        <div class="footer__contact">
          <a href="tel:{COMPANY['phone_href']}">{icon('phone', 17, 2.2)} {COMPANY['phone']}</a>
          <a href="mailto:{COMPANY['email']}">{icon('mail', 17, 2.2)} {COMPANY['email']}</a>
        </div>
      </div>
      <div>
        <h2>Services</h2>
        <ul>{svc_links}</ul>
      </div>
      <div>
        <h2>Service areas</h2>
        <ul>{area_links}<li><a href="{url('service-areas')}">All service areas</a></li></ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul>
          <li><a href="{url('about')}">About BM Industrial</a></li>
          <li><a href="{url('services')}">All services</a></li>
          <li><a href="{url('contact')}">Contact &amp; quotes</a></li>
          <li><a href="tel:{COMPANY['phone_href']}">24/7 emergency line</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bar">
      <p>&copy; <span id="year">2026</span> {esc(COMPANY['legal_name'])}. All rights reserved.</p>
      <p>{COMPANY['city']}, {COMPANY['state']} {COMPANY['zip']} · Serving SC, GA &amp; NC</p>
    </div>
  </div>
</footer>"""


# --------------------------------------------------------------------------
# Section builders
# --------------------------------------------------------------------------
def section_head(eyebrow=None, title=None, lead=None, center=False, wide=False, level=2):
    """Section intro.

    Left-aligned heads with supporting copy render as two columns, heading on
    the left and the lead on the right, which is how the reference site handles
    them and stops the right half of the section reading as dead space.
    """
    eyebrow_html = ""
    if eyebrow:
        c = "eyebrow eyebrow--center" if center else "eyebrow"
        eyebrow_html = f'<p class="{c}">{esc(eyebrow)}</p>'
    title_html = f'<h{level} class="display-2">{title}</h{level}>' if title else ""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""

    if lead and title and not center:
        return (f'<div class="section-head section-head--split reveal">'
                f'<div>{eyebrow_html}{title_html}</div><div>{lead_html}</div></div>')

    cls = "section-head"
    if center:
        cls += " section-head--center"
    if wide:
        cls += " section-head--wide"
    return f'<div class="{cls} reveal">{eyebrow_html}{title_html}{lead_html}</div>'


def crumbs(trail):
    """trail: list of (label, path or None)."""
    items = []
    for label, path in trail:
        if path is None:
            items.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
        else:
            items.append(f'<li><a href="{url(path)}">{esc(label)}</a></li>')
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(items)}</ol></nav>'


def service_card(s, tint=False):
    cls = "card card--link card--tint" if tint else "card card--link"
    return f"""<article class="{cls} reveal">
  <a class="card__hit" href="{url(s['path'])}" aria-label="{esc(s['title'])}"></a>
  <div class="card__icon">{icon(s['icon'], 26, 2)}</div>
  <h3 class="h4">{esc(s['card_title'])}</h3>
  <p>{s['short']}</p>
  <div class="card__foot"><span class="arrow-link">{esc(s.get('cta', 'Explore'))} {icon('arrow', 16, 2.4)}</span></div>
</article>"""


def services_grid(slugs=None, tint_index=None):
    items = SERVICES if slugs is None else [SERVICE_BY_SLUG[x] for x in slugs]
    cards = "".join(service_card(s, tint=(i == tint_index)) for i, s in enumerate(items))
    return f'<div class="grid grid--{4 if len(items) % 4 == 0 or len(items) > 3 else len(items)}">{cards}</div>'


def tag(text, variant="red"):
    return f'<span class="tag tag--{variant}">{esc(text)}</span>'


# Which tag variant reads correctly on each bento surface.
_TAG_ON = {"ink": "onink", "photo": "onink", "red": "onred"}


def bento_card(spec):
    """One colour-blocked panel. `title` and `body` may contain inline HTML."""
    surface = spec.get("surface", "bone")
    span = spec.get("span", 1)
    classes = ["bento__card", f"bento__card--w{span}", f"bento__card--{surface}", "reveal"]

    bg = ""
    if surface == "photo" and spec.get("photo"):
        slug, alt = spec["photo"]
        bg = f'<div class="bento__bg">{photo(slug, alt, sizes="(max-width: 680px) 100vw, 55vw")}</div>'

    media = ""
    if spec.get("media"):
        slug, alt = spec["media"]
        classes.append("has-media")
        media = f'<div class="bento__media">{photo(slug, alt, sizes="(max-width: 680px) 100vw, 32vw")}</div>'

    hit = ""
    if spec.get("path"):
        hit = f'<a class="hit" href="{url(spec["path"])}" aria-label="{esc(spec.get("aria") or _strip_tags(spec["title"]))}"></a>'

    tag_html = tag(spec["tag"], _TAG_ON.get(surface, "red")) if spec.get("tag") else ""

    cta_html = ""
    if spec.get("cta"):
        cta_html = (f'<div class="bento__cta"><span class="arrow-link">'
                    f'{esc(spec["cta"])} {icon("arrow", 16, 2.4)}</span></div>')

    return (f'<article class="{" ".join(classes)}">{hit}{bg}'
            f'<div class="bento__body">{tag_html}'
            f'<h3 class="bento__title">{spec["title"]}</h3>'
            f'<p>{spec["body"]}</p>{cta_html}</div>{media}</article>')


def bento(specs):
    return f'<div class="bento">{"".join(bento_card(s) for s in specs)}</div>'


def featurelist(items):
    """items: (icon_name, title, body_html). Deliberately no card chrome."""
    out = []
    for ic, title, body in items:
        out.append(
            f'<div class="featurelist__item reveal">'
            f'<div class="featurelist__icon">{icon(ic, 28, 2)}</div>'
            f'<h3>{esc(title)}</h3><p>{body}</p></div>'
        )
    return f'<div class="featurelist">{"".join(out)}</div>'


def promo_card(spec):
    surface = spec.get("surface", "ink")
    gear = ""
    if spec.get("gear", True):
        gear = (f'<img class="promo__gear" src="{BASE}/assets/img/logo/icon-color.png" '
                f'alt="" aria-hidden="true" loading="lazy" width="618" height="473">')
    tag_html = tag(spec["tag"], _TAG_ON.get(surface, "red")) if spec.get("tag") else ""
    href = spec["href"]
    if not href.startswith(("tel:", "mailto:", "http")):
        href = url(href)
    btn = spec.get("btn_class", "btn btn--light")
    return (f'<div class="promo promo--{surface} reveal">{gear}{tag_html}'
            f'<h3 class="promo__title">{spec["title"]}</h3><p>{spec["body"]}</p>'
            f'<div class="promo__btn"><a class="{btn}" href="{href}">{spec["label"]}</a></div></div>')


def promo_duo(a, b):
    return f'<div class="promo-duo">{promo_card(a)}{promo_card(b)}</div>'


def stats_block(items, ink=False):
    out = []
    for value, label in items:
        out.append(f'<div class="stat reveal"><p class="stat__num">{value}</p><p class="stat__label">{esc(label)}</p></div>')
    return f'<div class="stats">{"".join(out)}</div>'


def steps_block(items):
    """items: (icon_name, title, body)."""
    out = []
    for ic, title, body in items:
        out.append(
            f'<div class="step reveal">'
            f'<div class="step__icon">{icon(ic, 28, 2)}</div>'
            f'<h3 class="h4">{esc(title)}</h3><p>{body}</p></div>'
        )
    return f'<div class="steps">{"".join(out)}</div>'


def split(media_slug, alt, eyebrow, title, body_html, flip=False, cta=None):
    cls = "split split--flip reveal" if flip else "split reveal"
    cta_html = ""
    if cta:
        cta_html = f'<div class="btn-row"><a class="btn btn--outline" href="{url(cta[1])}">{esc(cta[0])}</a></div>'
    return f"""<div class="{cls}">
  <div class="split__media">{photo(media_slug, alt, sizes="(max-width: 860px) 100vw, 45vw")}</div>
  <div class="split__copy">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h3 class="display-3">{title}</h3>
    {body_html}
    {cta_html}
  </div>
</div>"""


def ticks(items):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<ul class="ticks">{lis}</ul>'


def band(media_slug, alt, eyebrow, title, lead, buttons_html=""):
    return f"""<div class="band reveal">
  <div class="band__bg">{photo(media_slug, alt, sizes="100vw")}</div>
  <div class="band__inner">
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h2 class="display-2">{title}</h2>
    <p class="lead">{lead}</p>
    {buttons_html}
  </div>
</div>"""


def brandwall(label="We service every major compressor platform"):
    lis = "".join(f"<li>{esc(b)}</li>" for b in BRANDS)
    return f"""<div class="brandwall">
  <div class="container">
    <p class="brandwall__label">{esc(label)}</p>
    <ul class="brandwall__list">{lis}</ul>
  </div>
</div>"""


def faq_block(items):
    out = []
    for q, a in items:
        out.append(
            f'<details><summary>{esc(q)}<span class="faq__icon" aria-hidden="true"></span></summary>'
            f'<div class="faq__body">{a}</div></details>'
        )
    return f'<div class="faq reveal">{"".join(out)}</div>'


def cta_panel(title, lead, primary=("Request a Quote", "contact"), secondary=True):
    sec = ""
    if secondary:
        sec = f'<a class="btn btn--on-dark btn--lg" href="tel:{COMPANY["phone_href"]}">{icon("phone", 18, 2.2)} {COMPANY["phone"]}</a>'
    gear = f'<img class="cta-panel__gear" src="{BASE}/assets/img/logo/icon-color.png" alt="" aria-hidden="true" loading="lazy" width="618" height="473">'
    return f"""<section class="section">
  <div class="container">
    <div class="cta-panel reveal">
      {gear}
      <div class="cta-panel__inner">
        <p class="eyebrow">Ready when you are</p>
        <h2 class="display-2">{title}</h2>
        <p class="lead">{lead}</p>
        <div class="btn-row" style="--ring-gap:var(--ink-900);--ring-line:#fff">
          <a class="btn btn--primary btn--lg btn--ring" href="{url(primary[1])}">{esc(primary[0])}</a>
          {sec}
        </div>
      </div>
    </div>
  </div>
</section>"""


def gallery(items):
    """items: list of (slug, alt)."""
    imgs = "".join(
        photo(s, a, sizes="(max-width: 500px) 100vw, (max-width: 860px) 50vw, 33vw")
        for s, a in items
    )
    return f'<div class="gallery reveal">{imgs}</div>'


def areas_grid(items=None, plain=False):
    items = items or AREAS
    out = []
    for a in items:
        cls = "area area--plain" if plain else "area"
        out.append(
            f'<a class="{cls}" href="{url(a["path"])}">'
            f'<span><span class="area__name">{esc(a["city"])}, {a["state"]}</span>'
            f'<span class="area__meta">{esc(a["meta"])}</span></span>'
            f'{icon("arrow", 18, 2.4)}</a>'
        )
    return f'<div class="areas reveal">{"".join(out)}</div>'


# --------------------------------------------------------------------------
# Structured data
# --------------------------------------------------------------------------
def local_business_schema():
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": SITE_URL + "/#business",
        "name": COMPANY["name"],
        "legalName": COMPANY["legal_name"],
        "url": SITE_URL + "/",
        "telephone": COMPANY["phone"],
        "email": COMPANY["email"],
        "image": SITE_URL + "/assets/img/og-image.jpg",
        "logo": SITE_URL + "/assets/img/logo/logo-full-color.png",
        "slogan": COMPANY["tagline"],
        "founder": {"@type": "Person", "name": COMPANY["owner"]},
        # No street address is published, so the schema stays at locality level
        # rather than repeating the town name as a street.
        "address": {
            "@type": "PostalAddress",
            "addressLocality": COMPANY["city"],
            "addressRegion": COMPANY["state"],
            "postalCode": COMPANY["zip"],
            "addressCountry": "US",
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00",
            "closes": "23:59",
        }],
        "areaServed": [{"@type": "State", "name": n} for n in ("South Carolina", "Georgia", "North Carolina")],
        "knowsAbout": BRANDS,
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Industrial services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["title"], "url": canonical(s["path"])}}
                for s in SERVICES
            ],
        },
    }


def faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": _strip_tags(a)},
            }
            for q, a in items
        ],
    }


def breadcrumb_schema(trail):
    out = []
    for i, (label, path) in enumerate(trail, start=1):
        entry = {"@type": "ListItem", "position": i, "name": label}
        if path is not None:
            entry["item"] = canonical(path)
        out.append(entry)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": out}


def _strip_tags(s):
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# --------------------------------------------------------------------------
# Document shell
# --------------------------------------------------------------------------
def document(title, description, path, body, active="", schemas=None, og_image=None):
    schema_tags = ""
    for s in (schemas or []):
        schema_tags += f'<script type="application/ld+json">{json.dumps(s, separators=(",", ":"))}</script>'

    og = og_image or (SITE_URL + "/assets/img/og-image.jpg")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical(path)}">
<meta name="theme-color" content="#231f20">
<meta name="format-detection" content="telephone=yes">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(COMPANY['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical(path)}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="{BASE}/assets/img/logo/favicon-32.png" sizes="32x32">
<link rel="icon" href="{BASE}/assets/img/logo/icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="{BASE}/assets/img/logo/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,500;0,600;0,700;0,800;1,700&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{BASE}/assets/css/site.css">
<script>if('IntersectionObserver' in window)document.documentElement.classList.add('reveal-on');</script>
{schema_tags}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{topbar()}
{nav(active)}
{drawer()}
<main id="main">
{body}
</main>
{footer()}
{callbar()}
<script src="{BASE}/assets/js/site.js" defer></script>
</body>
</html>
"""
