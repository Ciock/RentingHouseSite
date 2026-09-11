#!/usr/bin/env python3
"""
Pipeline immagini del Residence Roma Piacenza.

Prende le immagini "sorgente" in assets/img/ e ne genera in assets/img/opt/
le varianti responsive in AVIF e WebP, a più larghezze. L'HTML le usa tramite
<picture>: ogni browser scarica il formato migliore che supporta, alla
larghezza più vicina a quella che gli serve davvero.

    python3 tools/build-images.py            # rigenera tutto
    python3 tools/build-images.py --check    # verifica che sia aggiornato
    python3 tools/build-images.py --force    # rigenera anche ciò che è già a posto

DA RILANCIARE OGNI VOLTA CHE SI SOSTITUISCE UNA FOTO in assets/img/.
Se non lo si fa, il sito continua a mostrare la versione vecchia: per questo
il deploy su GitHub Actions esegue --check e si ferma se qualcosa è scaduto.

Oltre a generare le varianti, lo script:
  - rinomina in .jpg i sorgenti salvati come .jpeg / .JPG (e converte in JPEG
    quelli salvati come .png o .webp, lasciando l'originale al suo posto);
  - si ferma senza toccare nulla se manca un sorgente, invece di cancellarne
    le varianti;
  - riallinea in index.html srcset, width/height e preload: se una foto nuova
    ha una larghezza diversa dalla precedente, l'HTML si aggiorna da solo.

Dipendenze:  python3 -m pip install -r tools/requirements.txt
"""

import argparse
import hashlib
import json
import os
import re
import sys

from PIL import Image

try:
    import pillow_avif  # noqa: F401  (registra il codec AVIF in Pillow)
except ImportError:
    pass

Image.init()
HAS_AVIF = "AVIF" in Image.SAVE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "assets", "img")
OUT_DIR = os.path.join(SRC_DIR, "opt")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")
HTML = os.path.join(ROOT, "index.html")

# Estensioni accettate per un sorgente salvato con il nome giusto ma il formato
# "sbagliato". Le varianti JPEG vengono solo rinominate, le altre convertite.
JPEG_ALIASES = (".jpeg", ".JPG", ".JPEG", ".Jpg")
CONVERTIBLE = (".png", ".PNG", ".webp", ".WEBP")

# Larghezze richieste. Quelle più grandi del sorgente vengono scartate
# (non si ingrandisce mai un'immagine) e la larghezza del sorgente è
# sempre inclusa come variante massima.
TARGET_WIDTHS = (480, 960, 1440)

# Nessuna variante oltre questa larghezza, anche se il sorgente è più grande:
# le scansioni delle planimetrie arrivano a 2500 px, ma la card più larga del
# sito ne usa ~370 e la lightbox ~1100 su schermo retina.
MAX_WIDTH = 1600

# Solo le immagini di contenuto. Restano fuori:
#   og-image.jpg      -> le anteprime social vogliono un JPEG
#   apple-touch-icon  -> icona
#   favicon.svg       -> vettoriale
SOURCES = [
    "hero-camera.jpg",
    "camera-singola.jpg",
    "camera-doppia.jpg",
    "angolo-bar.jpg",
    "cucina-comune.jpg",
    "cortile-interno.jpg",
    "planimetria-camera-singola.jpg",
    "planimetria-camera-doppia.jpg",
    "planimetria-piano-primo.jpg",
    "planimetria-piano-secondo.jpg",
]

# Proporzioni con cui il CSS mostra le immagini ritagliate (object-fit: cover).
# Se una foto nuova se ne discosta più del 7% lo script avvisa, perché una
# parte dell'immagine verrà tagliata. Restano fuori, con None:
#   - l'hero, che si adatta alle proporzioni della foto (width/height vengono
#     riscritti in index.html da questo script);
#   - le planimetrie, mostrate intere con object-fit: contain.
EXPECTED_RATIO = {
    "hero-camera.jpg": None,
    "camera-singola.jpg": (3, 2),
    "camera-doppia.jpg": (3, 2),
    "angolo-bar.jpg": (3, 2),
    "cucina-comune.jpg": (3, 2),
    "cortile-interno.jpg": (3, 2),
    "planimetria-camera-singola.jpg": None,
    "planimetria-camera-doppia.jpg": None,
    "planimetria-piano-primo.jpg": None,
    "planimetria-piano-secondo.jpg": None,
}
RATIO_TOLERANCE = 0.07

AVIF_OPTS = {"quality": 52, "speed": 6}
WEBP_OPTS = {"quality": 76, "method": 6}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def widths_for(src_width):
    top = min(src_width, MAX_WIDTH)
    return sorted({w for w in TARGET_WIDTHS if w < top} | {top})


def variants(name, src_width):
    stem = os.path.splitext(name)[0]
    return [
        (w, fmt, f"{stem}-{w}.{fmt}")
        for w in widths_for(src_width)
        for fmt in ("avif", "webp")
    ]


def kb(n):
    return f"{n / 1024:.1f} KB"


def normalize_sources():
    """Porta a <nome>.jpg i sorgenti salvati con un'altra estensione.

    Restituisce la lista delle operazioni fatte, da mostrare all'utente.
    """
    done = []
    for name in SOURCES:
        target = os.path.join(SRC_DIR, name)
        if os.path.exists(target):
            continue
        stem = os.path.splitext(name)[0]

        for ext in JPEG_ALIASES:
            alt = os.path.join(SRC_DIR, stem + ext)
            if os.path.exists(alt):
                os.rename(alt, target)
                done.append(f"rinominato   {stem}{ext} -> {name}")
                break
        else:
            for ext in CONVERTIBLE:
                alt = os.path.join(SRC_DIR, stem + ext)
                if os.path.exists(alt):
                    with Image.open(alt) as im:
                        if im.mode in ("RGBA", "LA", "P"):
                            im = im.convert("RGBA")
                            bg = Image.new("RGB", im.size, (255, 255, 255))
                            bg.paste(im, mask=im.getchannel("A"))
                            im = bg
                        else:
                            im = im.convert("RGB")
                        im.save(target, "JPEG", quality=92, optimize=True,
                                progressive=True, subsampling=0)
                    done.append(f"convertito   {stem}{ext} -> {name}  "
                                f"(l'originale {stem}{ext} è rimasto: eliminalo se non serve)")
                    break
    return done


def html_sync(manifest, write):
    """Allinea index.html alle varianti realmente presenti nel manifest.

    Aggiorna, per ogni sorgente:
      - gli attributi srcset / imagesrcset che puntano alle sue varianti;
      - width e height del tag <img> di fallback;
      - data-src della lightbox (variante AVIF più grande).
    Restituisce solo le modifiche effettive. Con write=False non scrive nulla:
    serve a --check per capire se l'HTML è rimasto indietro.
    """
    if not os.path.exists(HTML):
        return []
    with open(HTML, encoding="utf-8") as fh:
        html = fh.read()
    changes = []

    def sub(pattern, build, label):
        nonlocal html

        def repl(m):
            new = build(m)
            if new != m.group(0):
                changes.append(label)
            return new

        html = re.sub(pattern, repl, html)

    for name, info in manifest.get("sources", {}).items():
        stem = os.path.splitext(name)[0]
        widths = sorted({int(v.rsplit("-", 1)[1].split(".")[0]) for v in info["variants"]})
        q = re.escape(stem)

        for fmt in ("avif", "webp"):
            entry = rf"\s*assets/img/opt/{q}-\d+\.{fmt}\s+\d+w\s*"
            wanted = ", ".join(f"assets/img/opt/{stem}-{w}.{fmt} {w}w" for w in widths)
            sub(rf'((?:image)?srcset=")(?:{entry}(?:,{entry})*)(")',
                lambda m, w=wanted: m.group(1) + w + m.group(2),
                f"srcset {fmt:4}   {stem}: {widths}")

        sub(rf'(<img src="assets/img/{q}\.jpg"\s+width=")\d+("\s+height=")\d+(")',
            lambda m, i=info: f'{m.group(1)}{i["width"]}{m.group(2)}{i["height"]}{m.group(3)}',
            f"width/height  {stem}: {info['width']}x{info['height']}")

        sub(rf'(data-src="assets/img/opt/{q}-)\d+(\.avif")',
            lambda m, w=max(widths): f"{m.group(1)}{w}{m.group(2)}",
            f"lightbox      {stem}: {max(widths)}px")

    if changes and write:
        with open(HTML, "w", encoding="utf-8") as fh:
            fh.write(html)
    # la stessa etichetta può comparire due volte (srcset di <source> e preload)
    return list(dict.fromkeys(changes))


def html_missing_refs():
    """Varianti citate in index.html che non esistono su disco."""
    if not os.path.exists(HTML):
        return []
    with open(HTML, encoding="utf-8") as fh:
        refs = set(re.findall(r"assets/img/opt/([\w.-]+\.(?:avif|webp))", fh.read()))
    return sorted(r for r in refs if not os.path.exists(os.path.join(OUT_DIR, r)))


def load_manifest():
    if not os.path.exists(MANIFEST):
        return None
    try:
        with open(MANIFEST, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def check():
    """Esce con codice 1 se le varianti non corrispondono ai sorgenti."""
    problems = []
    manifest = load_manifest()
    if manifest is None:
        problems.append("manifest.json mancante o illeggibile in assets/img/opt/")
        manifest = {"sources": {}}

    recorded = manifest.get("sources", {})

    for name in SOURCES:
        src = os.path.join(SRC_DIR, name)
        if not os.path.exists(src):
            stem = os.path.splitext(name)[0]
            alias = next((stem + e for e in JPEG_ALIASES + CONVERTIBLE
                          if os.path.exists(os.path.join(SRC_DIR, stem + e))), None)
            if alias:
                problems.append(f"{name}: salvato come {alias}, rilancia lo script per normalizzarlo")
            else:
                problems.append(f"{name}: sorgente mancante in assets/img/")
            continue

        digest = sha(src)
        if recorded.get(name, {}).get("sha") != digest:
            problems.append(f"{name}: modificata dopo l'ultima generazione")
            continue

        with Image.open(src) as im:
            src_width = im.width
        for _w, _fmt, out_name in variants(name, src_width):
            if not os.path.exists(os.path.join(OUT_DIR, out_name)):
                problems.append(f"{name}: manca la variante opt/{out_name}")

    extra = set(recorded) - set(SOURCES)
    for name in sorted(extra):
        problems.append(f"{name}: presente nel manifest ma non più fra i sorgenti")

    for ref in html_missing_refs():
        problems.append(f"index.html cita opt/{ref}, che non esiste")
    if not problems:
        for c in html_sync(manifest, write=False):
            problems.append(f"index.html non allineato: {c}")

    if problems:
        print("Le immagini ottimizzate NON sono aggiornate:\n")
        for p in problems:
            print(f"  - {p}")
        print("\nRigenerale con:  python3 tools/build-images.py")
        return 1

    print(f"Immagini ottimizzate aggiornate ({len(SOURCES)} sorgenti).")
    return 0


def build(force=False):
    if not HAS_AVIF:
        print(
            "Codec AVIF non disponibile.\n"
            "Installa le dipendenze con:\n"
            "  python3 -m pip install -r tools/requirements.txt\n\n"
            "L'HTML si aspetta i file .avif: senza codec le immagini non "
            "verrebbero mostrate su nessun browser moderno.",
            file=sys.stderr,
        )
        return 1

    for line in normalize_sources():
        print(f"  {line}")

    missing = [n for n in SOURCES if not os.path.exists(os.path.join(SRC_DIR, n))]
    if missing:
        # Fermarsi è l'unica scelta sicura: proseguire farebbe sparire le
        # varianti di questi sorgenti e l'HTML resterebbe a puntare a file
        # inesistenti.
        print("\nSorgenti mancanti, nessun file modificato:", file=sys.stderr)
        for m in missing:
            print(f"  - assets/img/{m}", file=sys.stderr)
        print("\nRimetti il file con quel nome (o togli la voce da SOURCES in "
              "questo script e il relativo <picture> da index.html).", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {"widths": list(TARGET_WIDTHS), "formats": ["avif", "webp"], "sources": {}}
    total_src = total_out = 0

    for name in SOURCES:
        src = os.path.join(SRC_DIR, name)
        with Image.open(src) as im:
            im = im.convert("RGB")
            src_w, src_h = im.size
            src_bytes = os.path.getsize(src)
            total_src += src_bytes

            ratio = EXPECTED_RATIO.get(name)
            if ratio:
                expected = ratio[0] / ratio[1]
                actual = src_w / src_h
                if abs(actual / expected - 1) > RATIO_TOLERANCE:
                    print(
                        f"  ATTENZIONE  {name}: proporzioni {src_w}x{src_h} "
                        f"({actual:.3f}) lontane da {ratio[0]}:{ratio[1]} "
                        f"({expected:.3f}): il sito ne mostrerà una parte "
                        f"ritagliata al centro."
                    )

            print(f"  {name}  ({src_w}x{src_h}, {kb(src_bytes)})")
            built = []
            for w, fmt, out_name in variants(name, src_w):
                out_path = os.path.join(OUT_DIR, out_name)
                if not force and os.path.exists(out_path) \
                        and os.path.getmtime(out_path) >= os.path.getmtime(src):
                    total_out += os.path.getsize(out_path)
                    built.append(out_name)
                    continue

                resized = im if w == src_w else im.resize(
                    (w, round(src_h * w / src_w)), Image.LANCZOS
                )
                opts = AVIF_OPTS if fmt == "avif" else WEBP_OPTS
                resized.save(out_path, fmt.upper(), **opts)
                total_out += os.path.getsize(out_path)
                built.append(out_name)

            largest = max(widths_for(src_w))
            for fmt in ("avif", "webp"):
                p = os.path.join(OUT_DIR, f"{os.path.splitext(name)[0]}-{largest}.{fmt}")
                print(f"      {fmt:4} {largest}px  {kb(os.path.getsize(p)):>9}"
                      f"   ({100 * os.path.getsize(p) / src_bytes:.0f}% del JPEG)")

            manifest["sources"][name] = {
                "sha": sha(src),
                "width": src_w,
                "height": src_h,
                "variants": built,
            }

    # Varianti rimaste da sorgenti rinominati o eliminati: vanno via, altrimenti
    # restano nel repository e nel deploy senza che nulla le referenzi.
    attese = {v for src in manifest["sources"].values() for v in src["variants"]}
    orfani = [f for f in sorted(os.listdir(OUT_DIR))
              if f.endswith((".avif", ".webp")) and f not in attese]
    for f in orfani:
        os.remove(os.path.join(OUT_DIR, f))
    if orfani:
        print(f"\nRimosse {len(orfani)} varianti orfane: "
              + ", ".join(orfani[:4]) + (" ..." if len(orfani) > 4 else ""))

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    n = sum(len(v["variants"]) for v in manifest["sources"].values())
    print(f"\n{n} varianti in assets/img/opt/  ({kb(total_out)} in totale)")
    print(f"Sorgenti JPEG: {kb(total_src)}")

    changes = html_sync(manifest, write=True)
    if changes:
        print("\nindex.html aggiornato:")
        for c in changes:
            print(f"  {c}")

    dangling = html_missing_refs()
    if dangling:
        print("\nindex.html cita varianti inesistenti:", file=sys.stderr)
        for d in dangling:
            print(f"  - opt/{d}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Genera le varianti AVIF/WebP del sito.")
    ap.add_argument("--check", action="store_true",
                    help="verifica che le varianti siano allineate ai sorgenti")
    ap.add_argument("--force", action="store_true",
                    help="rigenera anche le varianti già aggiornate")
    args = ap.parse_args()
    sys.exit(check() if args.check else build(force=args.force))
