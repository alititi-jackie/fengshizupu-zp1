#!/usr/bin/env python3
"""Build downloadable PDFs with the site header stamped on every page.

The pristine source PDFs stay untouched (archive + build inputs). This script
produces separate "-dl" PDFs: each page image is stamped with
「冯氏族谱 · fengshizupu.com」at the top-left (same position/colour logic as
scripts/render_pages.py) and reassembled into a PDF at the source page size.

Usage:
  python3 scripts/make_download_pdfs.py --books data/books.json \
      --pdf-dir <dir with <slug>-<volid>.pdf> --out <dir>
Output: <out>/<slug>-<volid>-dl.pdf  (plus a sizes report on stdout)
"""
import argparse
import io
import json
import os
import sys

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

STAMP_TEXT = "冯氏族谱 · fengshizupu.com"
RED = (116, 47, 50)
CREAM = (255, 244, 223)

FONT_CANDIDATES = [
    os.environ.get("STAMP_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
    os.path.expanduser("~/workspace/fengshizupu-work/book/fonts/NotoSerifSC-700.ttf"),
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def stamp(img):
    w, h = img.size
    size = max(18, int(w * 0.026))
    font = load_font(size)
    strip = img.crop((0, 0, int(w * 0.62), int(h * 0.055))).convert("L")
    px = list(strip.getdata())
    mean = sum(px) / max(1, len(px))
    color = CREAM if mean < 110 else RED
    d = ImageDraw.Draw(img)
    d.text((int(w * 0.024), int(h * 0.011)), STAMP_TEXT, font=font, fill=color)
    return img


def page_image(doc, page):
    imgs = page.get_images(full=True)
    if imgs:
        xref = max(imgs, key=lambda im: im[2] * im[3])[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    pix = page.get_pixmap(dpi=200)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def build(pdf_path, out_path):
    src = fitz.open(pdf_path)
    out = fitz.open()
    for page in src:
        img = stamp(page_image(src, page))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=88)
        new = out.new_page(width=page.rect.width, height=page.rect.height)
        new.insert_image(new.rect, stream=buf.getvalue())
    out.save(out_path, deflate=True, garbage=3)
    n = len(src)
    src.close()
    out.close()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.books, encoding="utf-8"))
    os.makedirs(args.out, exist_ok=True)
    for book in data["books"]:
        for vol in book["volumes"]:
            src = os.path.join(args.pdf_dir, f'{book["slug"]}-{vol["id"]}.pdf')
            dst = os.path.join(args.out, f'{book["slug"]}-{vol["id"]}-dl.pdf')
            n = build(src, dst)
            size = os.path.getsize(dst)
            print(f'{vol["id"]}: {n} pages, {size} bytes ({size/1048576:.1f} MB) -> {dst}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
