#!/usr/bin/env python3
"""Process source photography into optimised web assets, and build the social card.

Photos come from _inbox/ (git-ignored); the logo comes from brand/. Output lands in public/assets/img/.
Run from the project root:  python3 _build/images.py
"""
import os
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PHOTOS = os.path.join(ROOT, "_inbox", "photos")
OUT = os.path.join(ROOT, "public", "assets", "img")

# Widths emitted for every photo. The 400px step feeds the small card grids.
WIDTHS = [1800, 1200, 800, 400]
WEBP_Q = 80
JPEG_Q = 82

# slug -> (source filename, focal point as fraction of height)
# Focal point biases the crop so equipment stays in frame on wide aspect ratios.
PHOTOS = {
    # --- Air compressors -------------------------------------------------
    "compressor-warehouse-system": ("bm-industrial-solutions-industrial-air-compressor-system_2698.jpeg", 0.5),
    "compressor-exterior-install": ("bm-industrial-solutions-exterior-air-system-installation_0006.jpeg", 0.5),
    "compressor-dual-system": ("bm-industrial-solutions-dual-air-compressor-system_2786.jpeg", 0.5),
    "compressor-matched-pair": ("bm-industrial-solutions-lighting-retrofit-project-by-bm-industrial-solutions.jpg", 0.5),
    "compressor-gardner-denver-l37": ("bm-industrial-solutions-air-compressor-system_1089.jpeg", 0.45),
    "compressor-recip-and-rotary": ("bm-industrial-solutions-air-compressor-system_1438.jpeg", 0.5),
    "compressor-barn-airstation": ("bm-industrial-air-piping-with-multiple-valves.jpg", 0.5),
    "compressor-wall-retrofit": ("bm-industrial-exterior-wall-air-compressor-retrofit.jpg", 0.5),
    "compressor-metal-trades-site": ("bm-industrial-air-compressor-service.jpg", 0.5),
    "compressor-clean-facility": ("bm-industrial-solutions-commercial-air-compressor-system_2702.jpeg", 0.5),
    "compressor-rack-mounted-pair": ("bm-industrial-solutions-dual-air-compressor-system_0695.jpeg", 0.5),
    "compressor-controller-panel": ("bm-industrial-solutions-air-compressor-system_1092.jpeg", 0.45),
    "compressor-guarded-rotary": ("bm-industrial-solutions-air-compressor-system_2415.jpeg", 0.5),
    "compressor-warehouse-racking": ("bm-industrial-solutions-air-compressor-system-warehouse_2964.jpeg", 0.5),
    "compressor-tank-and-filter": ("bm-industrial-solutions-air-compressor-system_1088.jpeg", 0.5),
    "compressor-outdoor-canopy": ("bm-industrial-solutions-external-air-compressor-system_2475.jpeg", 0.5),
    "compressor-vintage-recip": ("IMG_0461.jpeg", 0.5),
    "compressor-ingersoll-dryer": ("IMG_0555.jpeg", 0.5),

    # --- Hydraulics ------------------------------------------------------
    "hydraulic-hose-bundle": ("IMG_1301.jpeg", 0.5),
    "hydraulic-cylinder-fittings": ("IMG_1292.jpeg", 0.5),
    "hydraulic-hauler-service": ("IMG_1303.jpeg", 0.5),
    "hydraulic-field-repair": ("IMG_1202.jpeg", 0.4),
    "hydraulic-system-inspection": ("bm-industrial-solutions-hydraulic-system-inspection-in-commercial-facility.jpg", 0.5),
    "hydraulic-forklift-service": ("IMG_0525.jpeg", 0.5),

    # --- Mechanical contracting -----------------------------------------
    "rigging-vessel-lift": ("bm-industrial-solutions-yellow-crane-lifting-mechanical-equipment_1550.jpeg", 0.45),
    "rigging-telehandler-container": ("bm-industrial-solutions-green-crane-lifting-shipping-container_1549.jpeg", 0.5),
    "rigging-forklift-equipment": ("bm-industrial-solutions-yellow-fork-lift-carrying-mechanical-equipment_1555.jpeg", 0.5),
    "mechanical-equipment-install": ("bm-industrial-solutions-mechanical-equipment-installation_2773.jpeg", 0.5),
    "mechanical-panel-wiring": ("bm-industrial-solutions-electrical-system-wiring_2770.jpeg", 0.5),
    "mechanical-blue-equipment": ("bm-industrial-solutions-electrical-panel-mechanical-equipment_2768.jpeg", 0.5),
    "fabrication-torch-cutting": ("IMG_0859.jpeg", 0.5),
    "fabrication-welding-shop": ("IMG_0871.jpeg", 0.5),
    "service-truck-trailer": ("IMG_1290.jpeg", 0.5),

    # --- Process piping & facility --------------------------------------
    "piping-blue-process-lines": ("bm-industrial-solutions-air-compressor-system_2031.jpeg", 0.5),
    "piping-air-lines-lighting": ("bm-industrial-air-lines-and-lighting-install.jpg", 0.5),
    "piping-conduit-install": ("bm-industrial-solutions-air-lines-and-electrical-conduit-installation.jpg", 0.5),
    "piping-exterior-enclosure": ("IMG_1324.jpeg", 0.5),
    "piping-white-conduit-room": ("IMG_0047.jpeg", 0.5),
    "facility-lighting-install": ("bm-industrial-solutions-industrial-lighting-installation_2695.jpeg", 0.5),
    "facility-lighting-lifts": ("bm-industrial-solutions-lighting-install-warehouse_2110.jpeg", 0.5),
    "facility-warehouse-beams": ("bm-industrial-warehouse-air-system-lighting.jpg", 0.5),
    "facility-dust-collector": ("IMG_0556.jpeg", 0.5),
}

BRAND_RED = (206, 23, 30)
BRAND_INK = (35, 31, 32)


def load(path):
    """Open an image with EXIF orientation applied."""
    im = Image.open(path)
    return ImageOps.exif_transpose(im).convert("RGB")


def emit_photo(slug, filename, focal):
    src = os.path.join(SRC_PHOTOS, filename)
    if not os.path.exists(src):
        print("  !! missing source:", filename)
        return 0
    im = load(src)
    made = 0
    for w in WIDTHS:
        if im.width < w and w != WIDTHS[-1]:
            # Never upscale, but always emit the smallest width.
            continue
        h = round(im.height * (w / im.width))
        rs = im.resize((w, h), Image.LANCZOS)
        rs.save(os.path.join(OUT, "photos", f"{slug}-{w}.webp"), "WEBP", quality=WEBP_Q, method=6)
        made += 1
    # One JPEG fallback for the rare client without WebP support.
    fb_w = min(1200, im.width)
    fb = im.resize((fb_w, round(im.height * (fb_w / im.width))), Image.LANCZOS)
    fb.save(os.path.join(OUT, "photos", f"{slug}.jpg"), "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    return made


def emit_og_image():
    """1200x630 social card: dark ground, photo bleed, logo and tagline."""
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), BRAND_INK)
    bg_src = os.path.join(SRC_PHOTOS, "bm-industrial-solutions-industrial-air-compressor-system_2698.jpeg")
    if os.path.exists(bg_src):
        bg = load(bg_src)
        scale = max(W / bg.width, H / bg.height)
        bg = bg.resize((round(bg.width * scale), round(bg.height * scale)), Image.LANCZOS)
        left = (bg.width - W) // 2
        top = (bg.height - H) // 2
        card.paste(bg.crop((left, top, left + W, top + H)))
        veil = Image.new("RGBA", (W, H), BRAND_INK + (214,))
        card = Image.alpha_composite(card.convert("RGBA"), veil).convert("RGB")

    # Reverse lockup from the logo kit (brand/): red gear, white wordmark.
    logo_path = os.path.join(ROOT, "brand", "png", "bm-horizontal-reverse-2000w.png")
    lg = Image.open(logo_path).convert("RGBA")
    tw = 640
    lg = lg.resize((tw, round(lg.height * (tw / lg.width))), Image.LANCZOS)
    card.paste(lg, (80, 170), lg)

    def font(name, size):
        for p in (f"/System/Library/Fonts/Supplemental/{name}.ttf",
                  f"/Library/Fonts/{name}.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    d = ImageDraw.Draw(card)
    d.rectangle([80, 396, 164, 402], fill=BRAND_RED)
    d.text((80, 428), "Locally Owned.  Personally Committed.  Professionally Built.",
           fill=(240, 240, 241), font=font("Arial Bold", 30))
    d.text((80, 476), "Air Compressors  ·  Hydraulics  ·  Mechanical Contracting  ·  Process Piping",
           fill=(163, 163, 166), font=font("Arial", 23))
    d.text((80, 524), "24/7 EMERGENCY SERVICE   ·   843-401-9670   ·   SC / GA / NC",
           fill=(232, 76, 82), font=font("Arial Bold", 23))
    card.save(os.path.join(OUT, "og-image.jpg"), "JPEG", quality=88, optimize=True)


def main():
    for sub in ("photos", "logo"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)

    print("Photos:")
    total = 0
    for slug, (fn, focal) in PHOTOS.items():
        n = emit_photo(slug, fn, focal)
        total += n
        print(f"  {slug:34s} {n} widths")
    print(f"  -> {total} webp derivatives + {len(PHOTOS)} jpeg fallbacks")

    # Logos and favicons come from the logo kit in brand/ and are copied into
    # public/assets/img/logo/ as-is; nothing to generate here.

    print("OG image:")
    emit_og_image()
    print("  done")


if __name__ == "__main__":
    main()
