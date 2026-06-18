#!/usr/bin/env python3
"""Generate web-optimized versions of the artwork photos.

Produces two sizes per image under photos/web/, each as JPEG + WebP:
  photos/web/<name>.{jpg,webp}        -> grid thumbnails  (<= 1100px long edge)
  photos/web/large/<name>.{jpg,webp}  -> lightbox / hero  (<= 1900px long edge)

The pages serve WebP first via <picture>/<source>, with the JPEG as fallback.

EXIF orientation is baked in (phone photos are rotated correctly), output is
progressive JPEG. Output filenames are lowercased with spaces -> hyphens so
they are safe on case-sensitive (Linux) hosts.

Usage:
    python optimize_images.py                # process the default set
    python optimize_images.py IMG_6450.JPG … # process specific files
"""
import os
import sys
from PIL import Image, ImageOps

BASE      = os.path.dirname(os.path.abspath(__file__))
SRC_DIR   = os.path.join(BASE, "photos", "Turarts")
OUT_DIR   = os.path.join(BASE, "photos", "web")
LARGE_DIR = os.path.join(OUT_DIR, "large")

GRID_MAX, GRID_Q   = 1100, 80
LARGE_MAX, LARGE_Q = 1900, 82
WEBP_Q             = 80   # WebP companion for each JPEG (<picture> serves it first)

# Images referenced by index.html + about.html (the curated set).
DEFAULT = [
    "About Me.jpg",
    "Untitled-1.jpg", "Untitled-2.jpg", "Untitled-3.jpg", "Untitled-4.jpg",
    "Untitled-5.jpg", "Untitled-11.jpg", "Untitled-12.jpg", "Untitled-13.jpg",
    "IMG_9845.JPG", "IMG_9846.JPG", "IMG_9848.JPG", "IMG_9849.JPG",
    "IMG_9852.JPG", "IMG_9853.JPG",
]


def out_name(filename: str) -> str:
    stem = os.path.splitext(filename)[0]
    return stem.lower().replace(" ", "-") + ".jpg"


def fit(im: Image.Image, max_edge: int) -> Image.Image:
    w, h = im.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    return im


def main(files):
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(LARGE_DIR, exist_ok=True)

    total_in = total_out = 0
    for fn in files:
        src = os.path.join(SRC_DIR, fn)
        if not os.path.exists(src):
            print(f"  MISSING  {fn}")
            continue
        try:
            im = Image.open(src)
            im = ImageOps.exif_transpose(im)
            im = im.convert("RGB")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR    {fn}: {e}")
            continue

        name = out_name(fn)
        gp = os.path.join(OUT_DIR, name)
        lp = os.path.join(LARGE_DIR, name)
        grid = fit(im, GRID_MAX)
        grid.save(gp, "JPEG", quality=GRID_Q, optimize=True, progressive=True)
        grid.save(gp[:-4] + ".webp", "WEBP", quality=WEBP_Q, method=6)
        large = fit(im, LARGE_MAX)
        large.save(lp, "JPEG", quality=LARGE_Q, optimize=True, progressive=True)
        large.save(lp[:-4] + ".webp", "WEBP", quality=WEBP_Q, method=6)

        in_kb  = os.path.getsize(src) / 1024
        out_kb = (os.path.getsize(gp) + os.path.getsize(lp)) / 1024
        total_in += in_kb
        total_out += out_kb
        print(f"  ok  {fn:24s} {in_kb/1024:6.1f}MB -> grid {os.path.getsize(gp)/1024:5.0f}KB + large {os.path.getsize(lp)/1024:5.0f}KB")

    print(f"\nTotal: {total_in/1024:.1f}MB source -> {total_out/1024:.1f}MB optimized "
          f"({100*(1-total_out/total_in):.0f}% smaller)" if total_in else "nothing processed")


if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else DEFAULT)
