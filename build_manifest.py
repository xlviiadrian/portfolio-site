#!/usr/bin/env python3
"""
XLVII // Rolling Loud Archive — asset build pipeline
=====================================================

WHAT IT DOES
  Reads your raw assets from   source-assets/<category>/...
  and produces GitHub-Pages-friendly output in  assets/rl/ :
     - full/   web-optimized full images (max 2000px edge, WebP)
     - thumbs/ small grid thumbnails       (max 600px edge,  WebP)
     - manifest.json  (the gallery reads this — drives everything)

WHY
  GitHub Pages caps the PUBLISHED site at 1 GB and individual files at 100 MB.
  1000+ originals at full res would blow past that. This shrinks each asset
  ~10-30x while staying crisp, so 1000+ assets fit comfortably.

HOW TO ADD MORE ASSETS (the whole workflow)
  1. Drop new files into  source-assets/<category-name>/
     The subfolder name becomes the filter label in the gallery.
  2. Run:   python3 build_manifest.py
  3. Commit & push the changed files in  assets/rl/  (and rolling-loud.html once).
  It's INCREMENTAL — already-processed assets are skipped, so re-runs are fast
  even with thousands of files. Only new/changed ones get rebuilt.

REQUIREMENTS
  pip install Pillow
"""

import os, sys, json, hashlib, datetime
from PIL import Image, ImageOps

# ---------------------------------------------------------------- CONFIG ----
SOURCE_DIR   = "source-assets"        # where you drop raw assets (by subfolder)
OUT_DIR      = os.path.join("assets", "rolling-loud")
FULL_DIR     = os.path.join(OUT_DIR, "full")
THUMB_DIR    = os.path.join(OUT_DIR, "thumbs")
MANIFEST     = os.path.join(OUT_DIR, "manifest.json")

FULL_MAX_EDGE  = 2000     # longest side of the "full view" image (px)
THUMB_MAX_EDGE = 600      # longest side of the grid thumbnail (px)
FULL_QUALITY   = 82       # WebP quality for full images
THUMB_QUALITY  = 80       # WebP quality for thumbnails

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
# NOTE: video (.mp4/.mov) is intentionally NOT handled — see the README.
#       Host video on YouTube/Vimeo/Cloudflare Stream and embed it instead;
#       MP4s will eat your 100 GB/month Pages bandwidth fast.
# ----------------------------------------------------------------------------


def asset_id(rel_path):
    """Stable short id from the file's path inside source-assets."""
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:12]


def ratio_bucket(w, h):
    """Snap to the aspect ratios you actually export so we can filter by them."""
    r = w / h
    buckets = {"9x16": 9 / 16, "4x5": 4 / 5, "1x1": 1.0,
               "4x3": 4 / 3, "16x9": 16 / 9, "3x4": 3 / 4, "2x3": 2 / 3}
    name = min(buckets, key=lambda k: abs(buckets[k] - r))
    return name if abs(buckets[name] - r) < 0.08 else f"{round(r,2)}:1"


def fit(img, max_edge):
    w, h = img.size
    if max(w, h) <= max_edge:
        return img
    scale = max_edge / max(w, h)
    return img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def newer(src, dst):
    """True if dst is missing or older than src (drives incremental builds)."""
    return (not os.path.exists(dst)) or os.path.getmtime(src) > os.path.getmtime(dst)


def human(nbytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


def main():
    if not os.path.isdir(SOURCE_DIR):
        sys.exit(f"!! No '{SOURCE_DIR}/' folder found. Create it and drop assets "
                 f"into subfolders, e.g. {SOURCE_DIR}/miami-2025/poster.jpg")

    os.makedirs(FULL_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    # gather source files
    files = []
    for root, _, names in os.walk(SOURCE_DIR):
        for n in sorted(names):
            if os.path.splitext(n)[1].lower() in VALID_EXT:
                files.append(os.path.join(root, n))
    files.sort()

    if not files:
        sys.exit(f"!! No images found in '{SOURCE_DIR}/'. Add some and re-run.")

    assets, categories = [], {}
    built, skipped, errors = 0, 0, 0

    for src in files:
        rel = os.path.relpath(src, SOURCE_DIR)
        parts = rel.split(os.sep)
        category = parts[0] if len(parts) > 1 else "uncategorized"
        aid = asset_id(rel)
        full_path  = os.path.join(FULL_DIR,  f"{aid}.webp")
        thumb_path = os.path.join(THUMB_DIR, f"{aid}.webp")

        try:
            if newer(src, full_path) or newer(src, thumb_path):
                with Image.open(src) as im:
                    im = ImageOps.exif_transpose(im).convert("RGB")
                    fit(im, FULL_MAX_EDGE).save(full_path,  "WEBP", quality=FULL_QUALITY,  method=6)
                    fit(im, THUMB_MAX_EDGE).save(thumb_path, "WEBP", quality=THUMB_QUALITY, method=6)
                built += 1
            else:
                skipped += 1

            with Image.open(full_path) as fim:
                w, h = fim.size

            ratio = ratio_bucket(w, h)
            categories[category] = categories.get(category, 0) + 1
            assets.append({
                "id": aid,
                "name": os.path.splitext(os.path.basename(src))[0],
                "category": category,
                "ratio": ratio,
                "w": w, "h": h,
                "thumb": f"assets/rolling-loud/thumbs/{aid}.webp",
                "full":  f"assets/rolling-loud/full/{aid}.webp",
            })
        except Exception as e:  # noqa
            errors += 1
            print(f"   skip (error): {rel} -> {e}")

    # newest categories tend to be most relevant; keep source order but sort
    # assets by category then name for a tidy grid
    assets.sort(key=lambda a: (a["category"], a["name"]))

    # If everything is a loose dump (no subfolders), don't emit filter chips.
    cat_list = [{"name": k, "count": v} for k, v in sorted(categories.items())]
    if cat_list == [{"name": "uncategorized", "count": len(assets)}]:
        cat_list = []

    manifest = {
        "title": "XLVII // Rolling Loud Archive",
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "count": len(assets),
        "categories": cat_list,
        "assets": assets,
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=1)

    # report + size guardrails against the 1 GB Pages cap
    out_size = sum(os.path.getsize(os.path.join(r, n))
                   for r, _, ns in os.walk(OUT_DIR) for n in ns)
    print("\n  XLVII // ROLLING LOUD — build complete")
    print(f"   assets:     {len(assets)}   (built {built}, skipped {skipped}, errors {errors})")
    print(f"   categories: {', '.join(c['name'] for c in manifest['categories'])}")
    print(f"   output size:{human(out_size)}  ({OUT_DIR}/)")
    if out_size > 0.9 * 1024**3:
        print("   ⚠️  Approaching the 1 GB GitHub Pages limit — see README for the CDN option.")
    print(f"   manifest:   {MANIFEST}\n")


if __name__ == "__main__":
    main()
