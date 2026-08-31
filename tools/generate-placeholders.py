#!/usr/bin/env python3
"""
Genera le immagini placeholder del Residence Roma Piacenza.

Uso:
    python3 tools/generate-placeholders.py

Ogni file viene scritto in assets/img/ con il NOME DEFINITIVO: per sostituire un
placeholder basta sovrascrivere il file con la foto/render reale mantenendo
lo stesso nome e le stesse proporzioni. Nessuna modifica all'HTML necessaria.

Richiede Pillow:  python3 -m pip install pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")

NAVY = (14, 33, 72)
NAVY_SOFT = (27, 53, 104)
GOLD = (245, 185, 33)
PAPER = (247, 248, 251)
INK = (107, 114, 128)

FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
]
FONT_CANDIDATES_REG = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]


def font(size, bold=False):
    for path in (FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REG):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def center(draw, xy, text, f, fill):
    box = draw.textbbox((0, 0), text, font=f)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2 - box[1]),
              text, font=f, fill=fill)


def placeholder(name, w, h, label, sublabel=""):
    """Placeholder chiaro, on-brand, con nome file e dimensioni consigliate."""
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)

    # righe diagonali tenui: si legge subito come "asset mancante"
    step = max(24, w // 40)
    for x in range(-h, w + h, step):
        d.line([(x, 0), (x + h, h)], fill=(232, 235, 242), width=max(2, w // 500))

    # cornice
    pad = max(12, w // 60)
    d.rectangle([pad, pad, w - pad, h - pad], outline=(214, 219, 230), width=max(2, w // 600))

    # blocco centrale
    bw, bh = int(w * 0.74), int(h * 0.46)
    bx, by = (w - bw) // 2, (h - bh) // 2
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=max(10, w // 80), fill=(255, 255, 255),
                        outline=(224, 228, 238), width=max(2, w // 700))

    cx = w // 2
    d.rounded_rectangle([cx - int(w * 0.055), by + int(bh * 0.13),
                         cx + int(w * 0.055), by + int(bh * 0.17)],
                        radius=max(3, w // 250), fill=GOLD)

    center(d, (cx, by + int(bh * 0.36)), label, font(max(16, int(w * 0.032)), bold=True), NAVY)
    if sublabel:
        center(d, (cx, by + int(bh * 0.56)), sublabel, font(max(12, int(w * 0.019))), INK)
    center(d, (cx, by + int(bh * 0.80)), f"{name}  ·  {w}x{h}px",
           font(max(11, int(w * 0.016))), INK)

    # etichetta d'angolo
    tag = "PLACEHOLDER — DA SOSTITUIRE"
    ft = font(max(10, int(w * 0.014)), bold=True)
    tb = d.textbbox((0, 0), tag, font=ft)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rounded_rectangle([pad * 2, pad * 2, pad * 2 + tw + pad * 2, pad * 2 + th + pad * 1.7],
                        radius=max(4, w // 200), fill=NAVY)
    d.text((pad * 3, pad * 2 + pad * 0.85 - tb[1]), tag, font=ft, fill=GOLD)

    img.save(os.path.join(OUT, name), "JPEG", quality=82, optimize=True, progressive=True)
    print(f"  ✓ {name}  ({w}x{h})")


def og_image(name="og-image.jpg", w=1200, h=630):
    """Anteprima social: NON è un placeholder, è utilizzabile così com'è."""
    img = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(img)
    for i in range(h):
        t = i / h
        d.line([(0, i), (w, i)],
               fill=tuple(int(NAVY[k] + (NAVY_SOFT[k] - NAVY[k]) * t) for k in range(3)))
    d.ellipse([w - 260, -190, w + 190, 260], outline=GOLD, width=3)
    d.ellipse([w - 150, -120, w + 240, 270], outline=(255, 255, 255, 40), width=2)
    d.rectangle([0, h - 14, w, h], fill=GOLD)

    d.text((80, 150), "RESIDENCE", font=font(76, bold=True), fill=(255, 255, 255))
    d.text((80, 236), "ROMA", font=font(76, bold=True), fill=GOLD)
    d.text((330, 254), "PIACENZA", font=font(44, bold=True), fill=(255, 255, 255))
    d.rectangle([82, 344, 152, 350], fill=GOLD)
    d.text((80, 380), "Camere per studenti · Via Roma 324, Piacenza",
           font=font(30), fill=(226, 231, 240))
    d.text((80, 432), "LIVE  ·  STUDY  ·  CONNECT.", font=font(24, bold=True), fill=GOLD)

    img.save(os.path.join(OUT, name), "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  ✓ {name}  ({w}x{h})")


def touch_icon(name="apple-touch-icon.png", size=180):
    img = Image.new("RGB", (size, size), NAVY)
    d = ImageDraw.Draw(img)
    f = font(int(size * 0.62), bold=True)
    center(d, (size * 0.46, size * 0.46), "R", f, (255, 255, 255))
    d.rectangle([size * 0.66, size * 0.60, size * 0.80, size * 0.66], fill=GOLD)
    img.save(os.path.join(OUT, name), "PNG", optimize=True)
    print(f"  ✓ {name}  ({size}x{size})")


IMAGES = [
    # (file, w, h, titolo, sottotitolo)
    ("hero-camera.jpg", 1600, 1067, "RENDER HERO — CAMERA",
     "Render fotorealistico della camera, formato orizzontale 3:2"),
    ("camera-singola.jpg", 1200, 800, "CAMERA SINGOLA",
     "Render della camera singola con bagno privato e angolo bar"),
    ("camera-doppia.jpg", 1200, 800, "CAMERA DOPPIA",
     "Render della camera doppia con bagno privato e angolo bar"),
    ("angolo-bar.jpg", 1200, 800, "ANGOLO BAR IN CAMERA",
     "Dettaglio di frigorifero e piano cottura per pasti semplici"),
    ("cucina-comune.jpg", 1200, 800, "CUCINA E SALA COMUNE",
     "Spazio condiviso per studiare e socializzare"),
    ("cortile-interno.jpg", 1200, 800, "CORTILE INTERNO PRIVATO",
     "Cortile privato del residence"),
    # Formato verticale 5:7, come le scansioni A4 delle planimetrie reali.
    ("planimetria-camera-singola.jpg", 900, 1260, "PLANIMETRIA — CAMERA SINGOLA",
     "Disegno tecnico o render 2D della camera singola"),
    ("planimetria-camera-doppia.jpg", 900, 1260, "PLANIMETRIA — CAMERA DOPPIA",
     "Disegno tecnico o render 2D della camera doppia"),
    # ATTENZIONE: planimetria-piano-primo.jpg e planimetria-piano-secondo.jpg
    # NON sono in questa lista perché sono planimetrie reali fornite dal cliente.
    # Rilanciare questo script non le sovrascrive.
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Genero i placeholder in assets/img/ …")
    for args in IMAGES:
        placeholder(*args)
    og_image()
    touch_icon()
    print("Fatto.")
    print("\nOra rigenera le varianti AVIF/WebP:")
    print("  python3 tools/build-images.py")
