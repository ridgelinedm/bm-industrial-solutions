#!/usr/bin/env python3
"""Static site generator for BM Industrial Solutions.

    python3 _build/build.py                     # GitHub Pages project URL
    python3 _build/build.py --base "" --site-url https://www.bmindustrialsolutionsllc.com

`--base` is the path prefix the site is served from. A project page lives at
/<repo>/ so it needs a prefix; a custom domain serves from the root so it does
not. Re-run this after changing content.py.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import render as R  # noqa: E402
from content import (  # noqa: E402
    COMPANY, SERVICES, SERVICE_BY_SLUG, PILLARS, AREAS, AREA_BY_SLUG,
    EXTENDED_AREAS, REVIEWS,
)

# Directories the build owns and will clear before writing.
GENERATED_DIRS = ["services", "service-areas", "about", "contact"]


# --------------------------------------------------------------------------
# Shared blocks
# --------------------------------------------------------------------------
def reviews_section(limit=12, alt=True, title=None, lead=None):
    """Google reviews imported by _build/reviews.py. Renders nothing if empty."""
    revs = REVIEWS.get("reviews") or []
    if not revs:
        return ""

    avg = REVIEWS.get("average")
    total = REVIEWS.get("total") or REVIEWS.get("count") or len(revs)

    if title is None:
        title = "What customers actually <em>say</em>"
    if lead is None:
        if avg and total:
            lead = (f"{total} reviews on Google, averaging {avg} out of 5. "
                    "Pulled straight from our Google Business Profile.")
        else:
            lead = "Pulled straight from our Google Business Profile."

    cards = []
    for r in revs[:limit]:
        initials = "".join(p[0] for p in r["name"].split()[:2] if p[:1].isalpha()).upper() or "G"
        meta = "Google review" + (f", {r['date']}" if r.get("date") else "")
        cards.append(
            f'<article class="review">{R.stars(r["rating"])}'
            f'<p>{R.esc(r["text"])}</p>'
            f'<div class="review__by">'
            f'<span class="review__avatar" aria-hidden="true">{R.esc(initials)}</span>'
            f'<span><span class="review__name">{R.esc(r["name"])}</span>'
            f'<span class="review__meta">{R.esc(meta)}</span></span></div></article>'
        )

    summary = ""
    if avg:
        summary = f"""<div class="reviews__summary reveal">
      <span class="reviews__score">{avg}</span>
      <span class="reviews__scoremeta">
        {R.stars(avg)}
        <span class="reviews__count"><strong>{total} reviews</strong> on Google</span>
      </span>
      <a class="btn btn--outline" href="{COMPANY['google_reviews_url']}" target="_blank" rel="noopener">Read them on Google {R.icon('arrow', 16, 2.4)}</a>
    </div>"""

    cls = "section section--alt" if alt else "section"
    return f"""<section class="{cls}">
  <div class="container">
    {R.section_head("Reviews", title, lead)}
    {summary}
    <div class="reviews__grid reveal">{''.join(cards)}</div>
  </div>
</section>"""


# Bento layout for the service lines. Sizes and surfaces are deliberately
# uneven. The asymmetry and the solid colour blocks are the whole point, and a
# row of five identical cards is exactly what this replaces.
BENTO_LAYOUT = {
    "services/air-compressor-services": dict(
        span=2, surface="ink", tag="Compressed air",
        title="Air compressor <em>systems</em>",
        media=("compressor-warehouse-system",
               "Rotary screw air compressor system and distribution piping in a manufacturing plant"),
    ),
    "services/hydraulics-services": dict(
        span=1, surface="red", tag="Hydraulics", title="Hydraulics",
    ),
    "services/mechanical-contracting": dict(
        span=1, surface="bone", tag="Mechanical", title="Mechanical <em>contracting</em>",
    ),
    "services/process-piping": dict(
        span=2, surface="photo", tag="Piping", title="Process <em>piping</em>",
        photo=("piping-blue-process-lines",
               "Industrial process piping with isolation valves and filtration vessels"),
    ),
    "services/preventive-maintenance": dict(
        span=2, surface="mist", tag="Stay ahead of it",
        title="Preventive <em>maintenance</em>",
        media=("compressor-matched-pair",
               "Matched pair of well-maintained rotary screw compressors under a maintenance agreement"),
    ),
}


def services_showcase(title, lead, eyebrow="What we do", alt=False):
    specs = []
    for p in PILLARS + ["services/preventive-maintenance"]:
        s = SERVICE_BY_SLUG[p]
        cfg = BENTO_LAYOUT[p]
        specs.append({
            "path": p,
            "aria": s["title"],
            "title": cfg["title"],
            "body": s["short"],
            "cta": "Explore",
            "tag": cfg.get("tag"),
            "span": cfg["span"],
            "surface": cfg["surface"],
            "media": cfg.get("media"),
            "photo": cfg.get("photo"),
        })
    cls = "section section--alt" if alt else "section"
    # Pages whose hero already states the heading pass None and get a bare grid.
    head = R.section_head(eyebrow, title, lead) if (title or lead or eyebrow) else ""
    return f"""<section class="{cls}">
  <div class="container">
    {head}
    {R.bento(specs)}
  </div>
</section>"""


def emergency_band():
    return f"""<section class="section section--tight">
  <div class="container container--wide">
    {R.band(
        "fabrication-welding-shop",
        "Technician working on industrial equipment during an after-hours emergency call",
        "24/7 emergency service",
        "When it fails at 2am, you still get a technician",
        "Breakdowns do not respect business hours. Our emergency line runs 24 hours a day, seven days a week. You reach someone who can diagnose the problem and dispatch a technician.",
        f'<div class="btn-row"><a class="btn btn--primary btn--lg" href="tel:{COMPANY["phone_href"]}">{R.icon("phone", 18, 2.2)} {COMPANY["phone"]}</a>'
        f'<a class="btn btn--on-dark btn--lg" href="{R.url("contact")}">Request a Quote</a></div>'
    )}
  </div>
</section>"""


def related_services(current_path, heading="Other services"):
    others = [SERVICE_BY_SLUG[p] for p in PILLARS if p != current_path][:3]
    if not others:
        return ""
    cards = "".join(R.service_card(s) for s in others)
    return f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("One vendor", heading, "Most of our customers started with one of these and consolidated the rest. Fewer vendors, fewer handoffs, one number when something breaks.")}
    <div class="grid grid--3">{cards}</div>
  </div>
</section>"""


def areas_strip(exclude=None, alt=True):
    items = [a for a in AREAS if a["path"] != exclude]
    extra = ", ".join(f"{c}, {s}" for c, s in EXTENDED_AREAS)
    cls = "section section--alt" if alt else "section"
    return f"""<section class="{cls}">
  <div class="container">
    {R.section_head("Where we work", "Field service across three states",
                    "Based in Holly Hill, South Carolina, with regular field service throughout South Carolina, Georgia and North Carolina.")}
    {R.areas_grid(items)}
    <p class="muted" style="margin-top:2rem;font-size:var(--fs-sm)">We also cover {R.esc(extra)} and the surrounding industrial areas. If you are outside these markets, <a href="{R.url('contact')}" style="color:var(--red);text-decoration:underline;text-underline-offset:3px">ask anyway</a>. We travel for the right project.</p>
  </div>
</section>"""


# --------------------------------------------------------------------------
# Home
# --------------------------------------------------------------------------
def page_home():
    hero = f"""<section class="hero">
  <div class="container">
    <div class="hero__grid">
      <div class="hero__copy">
        <p class="eyebrow">Industrial service · SC · GA · NC</p>
        <h1 class="display-1">Your plant runs on air, oil and pressure. We keep all three <em>moving</em>.</h1>
        <p class="lead">Air compressors, hydraulics, mechanical contracting and process piping from one owner-operated crew, with a 24/7 emergency line that a technician actually answers.</p>
        <div class="btn-row">
          <a class="btn btn--primary btn--lg" href="{R.url('contact')}">Request a Quote</a>
          <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
        </div>
        <ul class="hero__trust">
          <li>Owner-operated</li>
          <li>All major compressor brands</li>
          <li>24/7 emergency response</li>
        </ul>
      </div>
      <div class="hero__media">
        {R.photo("compressor-warehouse-system",
                 "Industrial rotary screw air compressor system and process piping installed in a manufacturing plant",
                 sizes="(max-width: 900px) 100vw, 46vw", loading="eager", fetchpriority="high")}
        <div class="hero__badge">
          <span class="hero__badge-num">24/7</span>
          <span class="hero__badge-txt"><strong>Emergency service</strong>Nights, weekends and holidays</span>
        </div>
      </div>
    </div>
  </div>
</section>"""

    stats = f"""<section class="section section--tight">
  <div class="container">
    {R.stats_block([
        ("<em>4</em>", "Service lines under one contractor: air, hydraulics, mechanical and piping"),
        ("<em>3</em>", "States covered by regular field service: South Carolina, Georgia and North Carolina"),
        ("<em>10+</em>", "Years of hands-on technician experience behind every job we take"),
        ("<em>1</em>", "Phone number, one point of contact, and the owner on the other end of it"),
    ])}
  </div>
</section>"""

    why = f"""<section class="section">
  <div class="container">
    {R.section_head("Why plants consolidate with us",
                    "Four trades, one contractor, <em>nobody to point at</em>",
                    "When compressed air, hydraulics, rigging and piping are split across four vendors, every problem lands in the gap between them. We close the gap by covering all four.")}
    {R.split(
        "rigging-vessel-lift",
        "Crane lifting a large industrial vessel into position during an equipment installation",
        "One vendor for everything",
        "The install, the piping and the service, all one crew",
        "<p class='lead'>A compressor installation is really four jobs: setting the equipment, piping the distribution, connecting the utilities and commissioning the system.</p>"
        "<p>Split those across separate contractors and you own the coordination risk. We take the whole scope, which means when something needs adjusting six months later, there is one number to call and no argument about whose scope it was.</p>",
        cta=("See all services", "services"),
    )}
    {R.split(
        "hydraulic-field-repair",
        "Technician carrying out a hydraulic repair on heavy equipment in the field",
        "Owner-operated",
        "You talk to the person doing the work",
        "<p>BM Industrial Solutions is run by " + COMPANY["owner"] + ", a hands-on technician with over a decade in the field. There is no service manager relaying messages between you and a technician who has never seen your plant.</p>"
        "<p>That has a practical consequence: the person who quotes the job is the person accountable for it, and decisions get made on the floor where the work is.</p>",
        flip=True,
    )}
  </div>
</section>"""

    steps = f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("How it works", "No mystery, no runaround",
                    "The same process whether it is a 2am breakdown or a planned installation.")}
    {R.steps_block([
        ("phone", "You call", "One number, answered 24/7. Tell us what stopped and we will tell you what it likely is and when we can be there."),
        ("search", "We diagnose", "On site, we work the whole system, so the repair addresses whatever caused the failure."),
        ("list", "You get options", "Repair cost, replacement cost and the reasoning behind our recommendation. The decision stays yours."),
        ("file", "We finish and document", "The work gets completed, tested and written up, so you know what was done and what to watch."),
    ])}
  </div>
</section>"""

    pm = f"""<section class="section">
  <div class="container">
    {R.promo_duo(
        {
            "surface": "ink",
            "tag": "Stay ahead of it",
            "title": "Nearly every emergency we get called to was <em>preventable</em>",
            "body": "Scheduled inspections across your compressed air, hydraulic and mechanical equipment, on intervals set by your run hours, plus priority response on the day something fails anyway.",
            "label": "How agreements work",
            "href": "services/preventive-maintenance",
        },
        {
            "surface": "red",
            "tag": "Down right now?",
            "title": "Stopped production does not wait for <em>business hours</em>",
            "body": "The emergency line runs 24 hours a day, seven days a week, including holidays. You reach someone who can diagnose and dispatch.",
            "label": f"Call {COMPANY['phone']}",
            "href": f"tel:{COMPANY['phone_href']}",
        },
    )}
  </div>
</section>"""

    faqs = [
        ("What areas do you cover?",
         f"<p>We are based in Holly Hill, South Carolina, and run regular field service across South Carolina, Georgia and North Carolina, including Charleston, North Charleston, Summerville, Columbia, Greenville, Spartanburg, Aiken, Sumter, Augusta, Savannah and the Charlotte area. <a href=\"{R.url('service-areas')}\">See all service areas</a>.</p>"),
        ("Do you really answer the phone at night?",
         f"<p>Yes. The emergency line runs 24 hours a day, including weekends and holidays. You reach someone who can assess the problem and dispatch. Call <a href=\"tel:{COMPANY['phone_href']}\">{COMPANY['phone']}</a>.</p>"),
        ("Which compressor brands do you service?",
         "<p>Gardner Denver, Sullair, Ingersoll Rand, Kaeser, Atlas Copco, CompAir/LeRoi, Quincy, Champion, Curtis and Saylor-Beall, plus most other platforms. We are independent, so the recommendation answers to your application.</p>"),
        ("Can you handle a whole project, or only service calls?",
         f"<p>Both. We do emergency repairs, scheduled maintenance, and complete installation projects including rigging, equipment setting and the process piping that connects it. <a href=\"{R.url('services/mechanical-contracting')}\">See mechanical contracting</a>.</p>"),
        ("Do you work around production schedules?",
         "<p>Routinely. Most installation and changeover work happens on weekends, night shifts or planned shutdowns so the disruptive part fits the window you actually have.</p>"),
    ]

    faq_section = f"""<section class="section">
  <div class="container container--narrow">
    {R.section_head("Questions", "Straight answers", center=True)}
    {R.faq_block(faqs)}
  </div>
</section>"""

    body = (
        hero
        + R.brandwall()
        + stats
        + services_showcase(
            "Everything your plant needs from <em>one contractor</em>",
            "Four service lines that overlap constantly in practice. Most customers start with one and consolidate the rest once they see how much coordination it removes.",
        )
        + emergency_band()
        + why
        + steps
        + pm
        + reviews_section()
        + areas_strip(alt=False)
        + faq_section
        + R.cta_panel(
            "Tell us what stopped working",
            "Send the details and we will come back with a straight answer on scope, timing and cost. If it is down right now, call instead and we will pick up.",
        )
    )

    return dict(
        path="",
        title="BM Industrial Solutions | Air Compressors & Hydraulics, SC GA NC",
        description="Owner-operated industrial service across SC, GA and NC. Air compressor repair, hydraulics, mechanical contracting and process piping. 24/7 emergency: 843-401-9670.",
        body=body,
        active="",
        schemas=[R.local_business_schema(), R.faq_schema(faqs)],
    )


# --------------------------------------------------------------------------
# Services hub
# --------------------------------------------------------------------------
def page_services():
    trail = [("Home", ""), ("Services", None)]

    hero = f"""<section class="pagehero pagehero--center">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow eyebrow--center">Services</p>
      <h1 class="display-1">Four trades. One contractor. <em>No gaps</em> between them.</h1>
      <p class="lead">Compressed air, hydraulics, mechanical contracting and process piping, plus preventive maintenance to keep all of it out of the emergency queue.</p>
      <div class="btn-row btn-row--center">
        <a class="btn btn--primary btn--lg" href="{R.url('contact')}">Request a Quote</a>
        <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
      </div>
    </div>
  </div>
</section>"""

    # The hero above already carries the heading, so the showcase runs bare.
    grid = services_showcase(None, None, eyebrow=None)

    triage = f"""<section class="section section--tight">
  <div class="container">
    {R.promo_duo(
        {
            "surface": "ink",
            "tag": "Start here",
            "title": "Not sure which one you <em>need</em>?",
            "body": "Most problems do not arrive neatly labelled. Water at the tool could be a dryer, a drain or the piping. Describe what is actually happening and we will work out which trade it belongs to.",
            "label": "Describe the problem",
            "href": "contact",
        },
        {
            "surface": "red",
            "tag": "Already know?",
            "title": "Skip straight to a <em>quote</em>",
            "body": "Equipment make and model, what it is doing, and how urgent it is. That is enough for us to come back with scope, timing and a number.",
            "label": f"Call {COMPANY['phone']}",
            "href": f"tel:{COMPANY['phone_href']}",
        },
    )}
  </div>
</section>"""

    # Sub-service breakdown for the two pillars that have children.
    sub_blocks = []
    for pillar_path in ("services/air-compressor-services", "services/hydraulics-services"):
        parent = SERVICE_BY_SLUG[pillar_path]
        kids = [SERVICE_BY_SLUG[c] for c in parent.get("children", [])]
        cards = "".join(f"""<article class="card card--link card--outline reveal">
  <a class="card__hit" href="{R.url(k['path'])}" aria-label="{R.esc(k['title'])}"></a>
  <div class="card__icon">{R.icon(k['icon'], 26, 2)}</div>
  <h3 class="h4">{R.esc(k['card_title'])}</h3>
  <p>{k['short']}</p>
  <div class="card__foot"><span class="arrow-link">Read more {R.icon('arrow', 16, 2.4)}</span></div>
</article>""" for k in kids)
        sub_blocks.append(f"""<div class="reveal" style="margin-top:clamp(2.5rem,1rem + 4vw,4rem)">
  <h3 class="display-3" style="margin-bottom:1.75rem">{R.esc(parent['card_title'])} in detail</h3>
  <div class="grid grid--3">{cards}</div>
</div>""")

    subs = f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("Going deeper", "Specific work, specific pages",
                    "Air compressors and hydraulics each break down into repair, installation and scheduled maintenance. If you already know what you need, go straight to it.")}
    {''.join(sub_blocks)}
  </div>
</section>"""

    faqs = [
        ("Do we have to use you for all four services?",
         "<p>No. Plenty of customers use us only for compressed air. The four lines exist because they overlap constantly in practice, but you are not obligated to consolidate anything.</p>"),
        ("Are you a dealer for a particular manufacturer?",
         "<p>No, and that is deliberate. Being independent means we can recommend the equipment your application actually calls for.</p>"),
        ("Can you quote a project from drawings?",
         f"<p>We can start from drawings, but for anything involving existing plant we will want a site walk before committing to a number. Send what you have through the <a href=\"{R.url('contact')}\">contact form</a> and we will tell you what else we need.</p>"),
        ("How do you charge?",
         "<p>Service work is quoted on time and materials with the rate structure given up front. Projects and installations are quoted as a fixed scope after a site visit. Either way you know the basis before we start.</p>"),
    ]

    body = (
        hero
        + R.brandwall()
        + grid
        + triage
        + subs
        + emergency_band()
        + f"""<section class="section">
  <div class="container">
    {R.section_head("How it works", "The same process every time",
                    "Whether it is an emergency call or a planned installation.")}
    {R.steps_block([
        ("phone", "You call", "One number, answered 24/7, by someone who can actually assess the problem."),
        ("search", "We diagnose", "The whole system gets checked, top to bottom."),
        ("list", "You get options", "Repair versus replace, with the reasoning and the cost of each."),
        ("file", "We finish and document", "Tested, commissioned and written up before we leave."),
    ])}
  </div>
</section>"""
        + f"""<section class="section section--alt">
  <div class="container container--narrow">
    {R.section_head("Questions", "Before you call", center=True)}
    {R.faq_block(faqs)}
  </div>
</section>"""
        + R.cta_panel(
            "Get a quote on any of it",
            "Describe the equipment and what it is doing. We will come back with scope, timing and a number, or tell you if it is not work we should be taking.",
        )
    )

    return dict(
        path="services",
        title="Services | Air, Hydraulics, Mechanical & Piping | BM Industrial",
        description="Air compressor service, hydraulics, mechanical contracting, process piping and preventive maintenance across SC, GA and NC. Owner-operated, 24/7 emergency response.",
        body=body,
        active="services",
        schemas=[R.breadcrumb_schema(trail), R.faq_schema(faqs)],
    )


# --------------------------------------------------------------------------
# Individual service pages
# --------------------------------------------------------------------------
def page_service(s):
    parent = SERVICE_BY_SLUG.get(s.get("parent"))
    trail = [("Home", ""), ("Services", "services")]
    if parent:
        trail.append((parent["card_title"], parent["path"]))
    trail.append((s["card_title"], None))

    hero = f"""<section class="pagehero">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow">{R.esc(parent['card_title'] if parent else 'Service')}</p>
      <h1 class="display-1">{R.esc(s['title'])}</h1>
      <p class="lead">{s['lead']}</p>
      <div class="btn-row">
        <a class="btn btn--primary btn--lg" href="{R.url('contact')}">Request a Quote</a>
        <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
      </div>
    </div>
  </div>
</section>"""

    ph_slug, ph_alt = s["hero_photo"]
    hero_img = f"""<section class="section--tight" style="padding-top:0">
  <div class="container container--wide">
    <div class="hero-strip reveal">
      {R.photo(ph_slug, ph_alt, sizes="100vw", loading="eager")}
    </div>
  </div>
</section>"""

    intro_paras = "".join(f"<p>{p}</p>" for p in s["intro"])
    overview = f"""<section class="section">
  <div class="container">
    <div class="split reveal">
      <div class="split__copy">
        <p class="eyebrow">Overview</p>
        <h2 class="display-3">{R.esc(s['card_title'])}</h2>
        <div class="prose">{intro_paras}</div>
      </div>
      <div class="split__copy">
        <h3 class="h4" style="margin-bottom:1.5rem">{R.esc(s['capabilities_title'])}</h3>
        {R.ticks(s['capabilities'])}
      </div>
    </div>
  </div>
</section>"""

    splits_html = ""
    if s.get("splits"):
        inner = []
        for sp in s["splits"]:
            body = sp["body"]
            if sp.get("extra_ticks"):
                body += R.ticks(sp["extra_ticks"])
            inner.append(R.split(sp["photo"][0], sp["photo"][1], sp["eyebrow"], sp["title"], body, flip=sp.get("flip", False)))
        splits_html = f"""<section class="section section--alt">
  <div class="container">{''.join(inner)}</div>
</section>"""

    children_html = ""
    if s.get("children"):
        kids = [SERVICE_BY_SLUG[c] for c in s["children"]]
        cards = "".join(f"""<article class="card card--link card--outline reveal">
  <a class="card__hit" href="{R.url(k['path'])}" aria-label="{R.esc(k['title'])}"></a>
  <div class="card__icon">{R.icon(k['icon'], 26, 2)}</div>
  <h3 class="h4">{R.esc(k['card_title'])}</h3>
  <p>{k['short']}</p>
  <div class="card__foot"><span class="arrow-link">Read more {R.icon('arrow', 16, 2.4)}</span></div>
</article>""" for k in kids)
        children_html = f"""<section class="section">
  <div class="container">
    {R.section_head("In detail", "Break it down further",
                    "If you already know what the job is, go straight to the specifics.")}
    <div class="grid grid--3">{cards}</div>
  </div>
</section>"""

    gallery_html = ""
    if s.get("gallery"):
        gallery_html = f"""<section class="section{' section--alt' if not children_html else ''}">
  <div class="container">
    {R.section_head("Recent work", "From the field",
                    "A sample of installations and service work across South Carolina, Georgia and North Carolina.")}
    {R.gallery(s['gallery'])}
  </div>
</section>"""

    brand_html = R.brandwall() if "air-compressor" in s["path"] else ""

    faq_html = f"""<section class="section">
  <div class="container container--narrow">
    {R.section_head("Questions", "About " + s['card_title'].lower(), center=True)}
    {R.faq_block(s['faqs'])}
  </div>
</section>"""

    up_link = ""
    if parent:
        up_link = f"""<section class="section section--tight">
  <div class="container">
    <a class="area area--plain reveal" href="{R.url(parent['path'])}" style="max-width:34rem">
      <span><span class="area__name">All {R.esc(parent['card_title'].lower())} services</span>
      <span class="area__meta">Back to the overview</span></span>
      {R.icon('arrow', 18, 2.4)}
    </a>
  </div>
</section>"""

    body = (
        hero + hero_img + overview + splits_html + children_html + brand_html
        + gallery_html + emergency_band() + faq_html + up_link
        + related_services(s["path"] if not parent else parent["path"])
        + R.cta_panel(
            "Get a quote for " + s["card_title"].lower(),
            "Tell us the equipment, the symptom and how urgent it is. We will come back with a straight answer. If it is down right now, call instead.",
        )
    )

    schemas = [
        R.breadcrumb_schema(trail),
        R.faq_schema(s["faqs"]),
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": s["title"],
            "serviceType": s["card_title"],
            "url": R.canonical(s["path"]),
            "description": s["meta_desc"],
            "provider": {"@id": R.SITE_URL + "/#business"},
            "areaServed": [{"@type": "State", "name": n} for n in ("South Carolina", "Georgia", "North Carolina")],
        },
    ]

    active = "services"
    return dict(
        path=s["path"],
        title=s["meta_title"],
        description=s["meta_desc"],
        body=body,
        active=active,
        schemas=schemas,
    )


# --------------------------------------------------------------------------
# Service areas
# --------------------------------------------------------------------------
def page_service_areas():
    trail = [("Home", ""), ("Service Areas", None)]
    extra = "".join(
        f'<li style="display:inline-block;margin:0 .5rem .5rem 0"><span style="display:inline-block;padding:.5rem 1.05rem;border:1px solid var(--border);border-radius:999px;font-family:var(--font-display);font-weight:700;color:var(--grey-600)">{R.esc(c)}, {s}</span></li>'
        for c, s in EXTENDED_AREAS
    )

    hero = f"""<section class="pagehero pagehero--center">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow eyebrow--center">Service areas</p>
      <h1 class="display-1">Field service across South Carolina, Georgia and North Carolina</h1>
      <p class="lead">Based in Holly Hill, South Carolina, close enough to the Lowcountry and the Midlands for same-day emergency response, and on the road regularly through the rest of the region.</p>
      <div class="btn-row btn-row--center">
        <a class="btn btn--primary btn--lg" href="{R.url('contact')}">Check your location</a>
        <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
      </div>
    </div>
  </div>
</section>"""

    main = f"""<section class="section">
  <div class="container">
    {R.section_head("Primary markets", "Where we work <em>most</em>",
                    "These are the areas we cover regularly, with dedicated pages for what each one tends to need.")}
    {R.areas_grid()}
  </div>
</section>"""

    more = f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("Also covered", "Beyond the core markets",
                    "We run field service throughout the region. These areas are covered on a scheduled basis. For emergencies, call and we will tell you honestly what we can do.")}
    <ul class="reveal">{extra}</ul>
    <p class="muted" style="margin-top:1.5rem;font-size:var(--fs-sm)">Somewhere else? <a href="{R.url('contact')}" style="color:var(--red);text-decoration:underline;text-underline-offset:3px">Ask anyway.</a> We travel for the right project, particularly installations and plant relocations.</p>
  </div>
</section>"""

    why = f"""<section class="section">
  <div class="container">
    {R.split(
        "service-truck-trailer",
        "BM Industrial Solutions service truck and equipment trailer at a job site",
        "A region we can cover",
        "Close enough to actually show up",
        "<p class='lead'>A national service network sounds reassuring right up until the nearest technician is four hours away and already on another call.</p>"
        "<p>We deliberately work a region we can cover properly. Holly Hill sits between the Lowcountry and the Midlands, which puts Charleston, North Charleston, Summerville, Columbia and Sumter all inside a comfortable response radius, and puts the rest of the Carolinas and Georgia within reach for scheduled work.</p>",
    )}
  </div>
</section>"""

    body = (
        hero + main + more + why
        + services_showcase(
            "The same four services everywhere we go",
            "Whatever market you are in, the scope does not change: air, hydraulics, mechanical contracting and process piping from one contractor.",
            eyebrow="What we bring", alt=True,
        )
        + emergency_band()
        + R.cta_panel(
            "Not sure if you are in range?",
            "Tell us where you are and what you need. If we are not the right people for the job, we will say so.",
        )
    )

    return dict(
        path="service-areas",
        title="Service Areas | SC, GA & NC Industrial Service | BM Industrial Solutions",
        description="Industrial field service across SC, GA and NC, covering Charleston, North Charleston, Summerville, Columbia, Greenville and Sumter. Call 843-401-9670.",
        body=body,
        active="service-areas",
        schemas=[R.breadcrumb_schema(trail)],
    )


def page_area(a):
    trail = [("Home", ""), ("Service Areas", "service-areas"), (f"{a['city']}, {a['state']}", None)]
    ph_slug, ph_alt = a["photo"]

    hero = f"""<section class="pagehero">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow">{R.esc(a['distance'])}</p>
      <h1 class="display-1">Industrial services in {R.esc(a['city'])}, {a['state']}</h1>
      <p class="lead">Air compressors, hydraulics, mechanical contracting and process piping. Owner-operated, with 24/7 emergency response across the {R.esc(a['city'])} area.</p>
      <div class="btn-row">
        <a class="btn btn--primary btn--lg" href="{R.url('contact')}">Request a Quote</a>
        <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
      </div>
    </div>
  </div>
</section>"""

    intro_paras = "".join(f"<p>{p}</p>" for p in a["intro"])
    overview = f"""<section class="section">
  <div class="container">
    <div class="split reveal">
      <div class="split__media">{R.photo(ph_slug, ph_alt, sizes="(max-width: 860px) 100vw, 45vw", loading="eager")}</div>
      <div class="split__copy">
        <p class="eyebrow">{R.esc(a['city'])}, {a['state']}</p>
        <h2 class="display-3">What we do here</h2>
        <div class="prose">{intro_paras}</div>
      </div>
    </div>
  </div>
</section>"""

    local = f"""<section class="section section--tint">
  <div class="container container--narrow">
    {R.section_head("Local conditions", "What tends to matter in " + a['city'],
                    "Every market has its own failure patterns. These are the ones we see most around here.")}
    <div class="reveal">{R.ticks(a['local'])}</div>
  </div>
</section>"""

    others = [x for x in AREAS if x["path"] != a["path"]]
    nearby = f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("Nearby", "Other areas we cover",
                    "Multi-site operations are straightforward for us to schedule, with one contractor across every location.")}
    {R.areas_grid(others)}
  </div>
</section>"""

    body = (
        hero + overview
        + services_showcase(
            f"Every service, available in {a['city']}",
            "The full scope travels with us. No sub-contracting the parts of the job that are inconvenient.",
            eyebrow="Services",
        )
        + local + emergency_band() + nearby
        + R.cta_panel(
            f"Need a technician in {a['city']}?",
            "Tell us the equipment and the symptom. If it is down right now, call. The emergency line runs 24 hours a day.",
        )
    )

    return dict(
        path=a["path"],
        title=a["meta_title"],
        description=a["meta_desc"],
        body=body,
        active="service-areas",
        schemas=[
            R.breadcrumb_schema(trail),
            {
                "@context": "https://schema.org",
                "@type": "Service",
                "name": f"Industrial services in {a['city']}, {a['state']}",
                "url": R.canonical(a["path"]),
                "description": a["meta_desc"],
                "provider": {"@id": R.SITE_URL + "/#business"},
                "areaServed": {"@type": "City", "name": a["city"], "addressRegion": a["state"]},
            },
        ],
    )


# --------------------------------------------------------------------------
# About
# --------------------------------------------------------------------------
def page_about():
    trail = [("Home", ""), ("About", None)]

    hero = f"""<section class="pagehero">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow">About</p>
      <h1 class="display-1">Built on Experience in <em>South Carolina</em></h1>
      <p class="lead">BM Industrial Solutions is an owner-operated industrial service company in Holly Hill, South Carolina. The person who quotes your job is the person accountable for it.</p>
    </div>
  </div>
</section>"""

    owner = f"""<section class="section">
  <div class="container">
    {R.split(
        "hydraulic-field-repair",
        "Technician performing hands-on hydraulic repair work on equipment in the field",
        "The owner",
        R.esc(COMPANY["owner"]),
        "<p class='lead'>A hands-on technician with over a decade of experience, still in the field on the jobs the company takes.</p>"
        "<p>BM Industrial Solutions exists because industrial plants kept running into the same problem: the technician who knew the equipment worked for a company where you could never quite reach him, and the person you could reach had never seen your plant.</p>"
        "<p>Being owner-operated collapses that. There is no dispatch layer between the customer and the work, and no incentive to sell equipment the application does not need.</p>",
    )}
  </div>
</section>"""

    stats = f"""<section class="section section--ink">
  <div class="container">
    {R.section_head("What that means in practice", "Small company, <em>serious scope</em>",
                    "Enough capability to take the whole job, small enough that you always know who is doing it.")}
    {R.stats_block([
        ("<em>4</em>", "Service lines: compressed air, hydraulics, mechanical contracting and process piping"),
        ("<em>3</em>", "States covered by regular field service"),
        ("<em>10+</em>", "Years of hands-on technician experience"),
        ("<em>24/7</em>", "Emergency coverage, including weekends and holidays"),
    ])}
  </div>
</section>"""

    values = f"""<section class="section">
  <div class="container">
    {R.section_head("How we work", "Six commitments we actually <em>keep</em>",
                    "These are the reason customers consolidate work with us.")}
    {R.featurelist([
        ("user", "The owner picks up",
         "The person quoting the work is the person doing it or supervising it. Decisions get made on your floor while we are standing in it."),
        ("search", "Diagnosis before parts",
         "Swapping components until the symptom goes away is expensive and it does not hold. We work the system methodically and fix the cause, which is why we are not back next quarter for the same fault."),
        ("layers", "Independent of manufacturers",
         "We are not a dealer for anybody. The recommendation you get is based on what your application needs."),
        ("file", "Written down, handed over",
         "What was checked, what was changed, what the readings were and what is trending toward a problem. A record you can plan a budget against."),
        ("clock", "Answered around the clock",
         "The emergency line runs 24 hours a day, including weekends and holidays, because that is when equipment actually decides to fail."),
        ("truck", "The whole scope travels",
         "Air, hydraulics, rigging and piping arrive together. No sub-contracting the half of the job that is inconvenient."),
    ])}
  </div>
</section>"""

    work = f"""<section class="section section--alt">
  <div class="container">
    {R.section_head("Recent work", "What the days actually look like",
                    "Installations, retrofits, rigging and field repair across the Carolinas and Georgia.")}
    {R.gallery([
        ("rigging-vessel-lift", "Crane lifting a large industrial vessel during an equipment installation"),
        ("compressor-exterior-install", "Completed exterior compressed air system installation"),
        ("fabrication-torch-cutting", "Torch cutting during structural fabrication work"),
        ("facility-lighting-lifts", "Lifts positioned for overhead piping and facility installation work"),
        ("compressor-dual-system", "Dual rotary screw compressor installation with receiver tanks"),
        ("rigging-forklift-equipment", "Forklift moving large mechanical equipment inside a plant"),
    ])}
  </div>
</section>"""

    body = (
        hero + owner + stats + values + R.brandwall() + work
        + emergency_band()
        + reviews_section(limit=9)
        + areas_strip(alt=False)
        + R.cta_panel(
            "Work with a contractor who picks up the phone",
            "Tell us what you are dealing with. You will get a straight assessment, a realistic timeline and a number, from the person who will be doing the work.",
        )
    )

    return dict(
        path="about",
        title="About BM Industrial Solutions | Owner-Operated Industrial Service in SC",
        description="Owner-operated industrial service in Holly Hill, SC, led by Bradley McLaughlin. Air compressors, hydraulics, mechanical contracting and process piping across SC, GA and NC.",
        body=body,
        active="about",
        schemas=[R.breadcrumb_schema(trail), R.local_business_schema()],
    )


# --------------------------------------------------------------------------
# Contact
# --------------------------------------------------------------------------
def page_contact():
    trail = [("Home", ""), ("Contact", None)]

    service_options = "".join(
        f'<option value="{R.esc(s["card_title"])}">{R.esc(s["card_title"])}</option>'
        for s in SERVICES if s["path"] in PILLARS or s["path"] == "services/preventive-maintenance"
    )

    hero = f"""<section class="pagehero">
  <div class="container">
    <div class="pagehero__inner">
      {R.crumbs(trail)}
      <p class="eyebrow">Contact</p>
      <h1 class="display-1">Tell us what <em>stopped working</em></h1>
      <p class="lead">If equipment is down right now, call. The emergency line runs 24 hours a day and you will reach someone who can dispatch. For quotes, planned work and everything else, the form is the fastest route.</p>
    </div>
  </div>
</section>"""

    contact_block = f"""<section class="section" style="padding-top:clamp(1rem,0.5rem + 1.5vw,2rem)">
  <div class="container">
    <div class="contact-grid">
      <div class="reveal">
        <div class="contact-list">
          <a class="contact-item" href="tel:{COMPANY['phone_href']}">
            <span class="contact-item__icon">{R.icon('phone', 22, 2)}</span>
            <span>
              <span class="contact-item__label">24/7 emergency &amp; service</span>
              <span class="contact-item__value">{COMPANY['phone']}</span>
              <span class="contact-item__note">Nights, weekends and holidays included</span>
            </span>
          </a>
          <a class="contact-item" href="mailto:{COMPANY['email']}">
            <span class="contact-item__icon">{R.icon('mail', 22, 2)}</span>
            <span>
              <span class="contact-item__label">Email</span>
              <span class="contact-item__value" style="font-size:.95rem;word-break:break-all">{COMPANY['email']}</span>
              <span class="contact-item__note">Quotes, drawings and scheduling</span>
            </span>
          </a>
          <div class="contact-item">
            <span class="contact-item__icon">{R.icon('pin', 22, 2)}</span>
            <span>
              <span class="contact-item__label">Based in</span>
              <span class="contact-item__value">{COMPANY['city']}, {COMPANY['state']} {COMPANY['zip']}</span>
              <span class="contact-item__note">Field service across South Carolina, Georgia and North Carolina</span>
            </span>
          </div>
          <div class="contact-item">
            <span class="contact-item__icon">{R.icon('clock', 22, 2)}</span>
            <span>
              <span class="contact-item__label">Hours</span>
              <span class="contact-item__value">24 hours, 7 days</span>
              <span class="contact-item__note">Emergency response any time; scheduled work booked ahead</span>
            </span>
          </div>
        </div>

        <article class="card card--ink reveal" style="margin-top:1rem">
          <div class="card__icon">{R.icon('bolt', 26, 2)}</div>
          <h3 class="h4">Down right now?</h3>
          <p>Do not wait on the form. Call the emergency line. It is answered 24 hours a day, including weekends and holidays, and you will reach someone who can dispatch.</p>
          <div class="card__foot"><a class="btn btn--light btn--sm" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 16, 2.2)} Call {COMPANY['phone']}</a></div>
        </article>
      </div>

      <div class="reveal">
        <form class="form" data-contact-form
              data-endpoint="https://formspree.io/f/YOUR_FORM_ID"
              data-fallback-email="{COMPANY['email']}"
              method="POST" action="https://formspree.io/f/YOUR_FORM_ID">
          <h2 class="display-3" style="margin-bottom:.5rem">Request a quote</h2>
          <p class="muted" style="font-size:var(--fs-sm);margin-bottom:1.75rem">The more detail you give us, the more useful the first reply will be.</p>

          <div class="form__row">
            <label class="field">
              <span class="field__label">Name <span aria-hidden="true">*</span></span>
              <input type="text" name="name" autocomplete="name" required>
            </label>
            <label class="field">
              <span class="field__label">Company</span>
              <input type="text" name="company" autocomplete="organization">
            </label>
          </div>

          <div class="form__row">
            <label class="field">
              <span class="field__label">Phone <span aria-hidden="true">*</span></span>
              <input type="tel" name="phone" autocomplete="tel" required>
            </label>
            <label class="field">
              <span class="field__label">Email <span aria-hidden="true">*</span></span>
              <input type="email" name="email" autocomplete="email" required>
            </label>
          </div>

          <div class="form__row">
            <label class="field">
              <span class="field__label">Service needed</span>
              <select name="service">
                <option value="">Not sure / something else</option>
                {service_options}
              </select>
            </label>
            <label class="field">
              <span class="field__label">Urgency</span>
              <select name="urgency">
                <option value="Emergency (down now)">Emergency (down now)</option>
                <option value="Urgent (within a few days)">Urgent (within a few days)</option>
                <option value="Planned work" selected>Planned work</option>
                <option value="Budget pricing only">Budget pricing only</option>
              </select>
            </label>
          </div>

          <label class="field">
            <span class="field__label">Location (city, state)</span>
            <input type="text" name="location" autocomplete="address-level2">
          </label>

          <label class="field">
            <span class="field__label">What is happening? <span aria-hidden="true">*</span></span>
            <textarea name="message" required placeholder="Equipment make and model if you have it, what it is doing, when it started, and anything you have already tried."></textarea>
          </label>

          <div class="hp" aria-hidden="true">
            <label>Leave this field empty<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label>
          </div>

          <div class="btn-row" style="margin-top:1.5rem">
            <button class="btn btn--primary btn--lg" type="submit">Send request</button>
            <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} Call instead</a>
          </div>

          <div class="form__status" role="status" aria-live="polite"></div>
          <p class="form__note">We answer every enquiry within one business day, or immediately if you mark it an emergency.</p>
        </form>
      </div>
    </div>
  </div>
</section>"""

    faqs = [
        ("What information helps you quote fastest?",
         "<p>Equipment make and model, what it is doing (or not doing), when it started, your location, and whether production is stopped. A photo of the nameplate is worth several emails.</p>"),
        ("How quickly will you respond?",
         "<p>Within one business day for quotes and planned work. For emergencies, call rather than email. The line is answered 24 hours a day.</p>"),
        ("Do you charge for a site visit or quote?",
         "<p>For project work and installations, the site walk is part of quoting it properly. For diagnostic service calls, we tell you the rate structure before we dispatch so there are no surprises.</p>"),
        ("We are outside your listed service areas. Is it worth asking?",
         f"<p>Yes. We travel for the right project, particularly installations and plant relocations. <a href=\"{R.url('service-areas')}\">See where we work</a> and ask anyway if you are outside it.</p>"),
    ]

    body = (
        hero + contact_block
        + emergency_band()
        + f"""<section class="section">
  <div class="container container--narrow">
    {R.section_head("Before you send", "Common questions", center=True)}
    {R.faq_block(faqs)}
  </div>
</section>"""
        + areas_strip()
    )

    return dict(
        path="contact",
        title="Contact BM Industrial Solutions | 24/7 Emergency 843-401-9670",
        description="Request a quote or reach our 24/7 emergency line at 843-401-9670. Industrial service across South Carolina, Georgia and North Carolina from Holly Hill, SC.",
        body=body,
        active="contact",
        schemas=[R.breadcrumb_schema(trail), R.local_business_schema(), R.faq_schema(faqs)],
    )


# --------------------------------------------------------------------------
# 404
# --------------------------------------------------------------------------
def page_404():
    body = f"""<section class="pagehero pagehero--center" style="padding-block:clamp(4rem,2rem + 8vw,9rem)">
  <div class="container">
    <div class="pagehero__inner">
      <p class="eyebrow eyebrow--center">404</p>
      <h1 class="display-1">We couldn't find that page.</h1>
      <p class="lead">The link may be old, or the page may have moved. Everything we do is one of four things. Start there, or call and we will point you at it.</p>
      <div class="btn-row btn-row--center">
        <a class="btn btn--primary btn--lg" href="{R.url('services')}">Browse services</a>
        <a class="btn btn--outline btn--lg" href="tel:{COMPANY['phone_href']}">{R.icon('phone', 18, 2.2)} {COMPANY['phone']}</a>
      </div>
    </div>
  </div>
</section>""" + services_showcase(
        "What you were probably looking for",
        "Air compressors, hydraulics, mechanical contracting and process piping.",
        eyebrow="Services", alt=True,
    )

    return dict(
        path="404",
        title="Page not found | BM Industrial Solutions",
        description="That page could not be found. Browse our industrial services or call 843-401-9670.",
        body=body,
        active="",
        schemas=[],
    )


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------
def write_page(p):
    html = R.document(
        title=p["title"], description=p["description"], path=p["path"],
        body=p["body"], active=p.get("active", ""), schemas=p.get("schemas"),
    )
    if p["path"] == "404":
        dest = os.path.join(ROOT, "404.html")
    elif p["path"] == "":
        dest = os.path.join(ROOT, "index.html")
    else:
        d = os.path.join(ROOT, *p["path"].split("/"))
        os.makedirs(d, exist_ok=True)
        dest = os.path.join(d, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    return dest


def write_sitemap(pages):
    urls = []
    for p in pages:
        if p["path"] == "404":
            continue
        # Home and top-level hubs get more weight than deep leaves.
        depth = 0 if not p["path"] else p["path"].count("/") + 1
        priority = {0: "1.0", 1: "0.9", 2: "0.8"}.get(depth, "0.7")
        urls.append(
            f"  <url><loc>{R.canonical(p['path'])}</loc>"
            f"<changefreq>monthly</changefreq><priority>{priority}</priority></url>"
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_robots():
    txt = f"User-agent: *\nAllow: /\n\nSitemap: {R.SITE_URL}/sitemap.xml\n"
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


def clean():
    for d in GENERATED_DIRS:
        path = os.path.join(ROOT, d)
        if os.path.isdir(path):
            shutil.rmtree(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/bm-industrial-solutions",
                    help='Path prefix the site is served from ("" for a custom domain)')
    ap.add_argument("--site-url", default="https://ridgelinedm.github.io/bm-industrial-solutions",
                    help="Absolute site URL used for canonicals, sitemap and structured data")
    args = ap.parse_args()

    R.BASE = args.base.rstrip("/")
    R.SITE_URL = args.site_url.rstrip("/")

    clean()

    pages = [page_home(), page_services()]
    pages += [page_service(s) for s in SERVICES]
    pages.append(page_service_areas())
    pages += [page_area(a) for a in AREAS]
    pages += [page_about(), page_contact(), page_404()]

    for p in pages:
        dest = write_page(p)
        print("  ", os.path.relpath(dest, ROOT))

    write_sitemap(pages)
    write_robots()

    # GitHub Pages must not run these through Jekyll.
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    print(f"\n{len(pages)} pages written. base={R.BASE or '/'} site={R.SITE_URL}")


if __name__ == "__main__":
    main()
