# Residence Roma Piacenza — sito web

Landing page statica (one-page) per il **Residence Roma Piacenza**, residence per
studenti universitari in Via Roma 324, Piacenza.

HTML5 + CSS3 + JavaScript vanilla. **Nessun framework, nessun backend, nessun
database, nessuno step di build**: i file si aprono e si pubblicano così come sono.

---

## Indice

1. [Struttura dei file](#1-struttura-dei-file)
2. [Vedere il sito in locale](#2-vedere-il-sito-in-locale)
3. [Sostituire le immagini placeholder](#3-sostituire-le-immagini-placeholder)
4. [Sostituire il logo](#4-sostituire-il-logo)
5. [Cambiare il dominio (importante per la SEO)](#5-cambiare-il-dominio-importante-per-la-seo)
6. [Cambiare contatti, numero WhatsApp e testi](#6-cambiare-contatti-numero-whatsapp-e-testi)
7. [Aggiungere un form di contatto reale](#7-aggiungere-un-form-di-contatto-reale)
8. [Pubblicare il sito online](#8-pubblicare-il-sito-online)
9. [Checklist SEO dopo la pubblicazione](#9-checklist-seo-dopo-la-pubblicazione)
10. [Note tecniche e performance](#10-note-tecniche-e-performance)

---

## 1. Struttura dei file

```
.
├── index.html                  # tutta la pagina (7 sezioni + header/footer)
├── robots.txt                  # indicazioni per i motori di ricerca
├── sitemap.xml                 # mappa del sito per Google
├── site.webmanifest            # icona e nome se il sito viene "installato" da mobile
├── .nojekyll                   # GitHub Pages: serve i file senza elaborarli
├── .gitignore
├── README.md
├── assets/
│   ├── css/style.css           # unico foglio di stile
│   ├── js/main.js              # menu, animazioni, lightbox, mappa on-demand
│   └── img/                    # immagini sorgente (oggi PLACEHOLDER, vedi punto 3)
│       └── opt/                # varianti AVIF/WebP GENERATE - non modificare a mano
└── tools/
    ├── requirements.txt          # dipendenze degli script (non del sito)
    ├── generate-placeholders.py  # rigenera i placeholder
    └── build-images.py           # genera le varianti AVIF/WebP (vedi punto 3)
```

> `assets/img/opt/` è generata: si rigenera con un comando e va committata
> insieme al resto. Non modificare quei file a mano.

Le sezioni della pagina, nell'ordine, sono:
Hero → `#camere` → `#servizi` → `#planimetrie` → `#posizione` → `#contatti` → footer.

---

## 2. Vedere il sito in locale

Il modo più semplice: doppio click su `index.html`.

Per una anteprima identica a quella online (consigliata, perché alcuni browser
limitano i file aperti da disco), avvia un piccolo server locale dalla cartella
del progetto:

```bash
python3 -m http.server 4321
```

Poi apri **http://localhost:4321** nel browser. Per fermarlo: `Ctrl + C`.

---

## 3. Sostituire le immagini placeholder

Tutte le immagini attuali sono **placeholder generati automaticamente**: si
riconoscono dall'etichetta blu "PLACEHOLDER — DA SOSTITUIRE" in alto a sinistra.

> **Sostituire un'immagine = sovrascrivere il file mantenendo lo stesso nome.**
> Non serve toccare l'HTML.

Tieni le **stesse proporzioni** indicate, altrimenti l'immagine viene ritagliata
al centro (`object-fit: cover`).

| File in `assets/img/` | Cosa serve | Dimensioni consigliate | Proporzioni |
|---|---|---|---|
| `hero-camera.jpg` | Render principale di una camera (immagine di apertura) | 1600 × 1067 | 3:2 |
| `camera-singola.jpg` | Render della camera singola | 1200 × 800 | 3:2 |
| `camera-doppia.jpg` | Render della camera doppia | 1200 × 800 | 3:2 |
| `angolo-bar.jpg` | Dettaglio angolo bar / frigorifero in camera | 1200 × 800 | 3:2 |
| `cucina-comune.jpg` | Cucina e sala comune | 1200 × 800 | 3:2 |
| `cortile-interno.jpg` | Cortile interno privato | 1200 × 800 | 3:2 |
| `planimetria-camera-singola.jpg` | Planimetria camera singola | 900 × 1260 | 5:7 verticale |
| `planimetria-camera-doppia.jpg` | Planimetria camera doppia | 900 × 1260 | 5:7 verticale |
| `planimetria-piano-primo.jpg` | Planimetria del piano primo — **già reale** | scansione A4 | 5:7 verticale |
| `planimetria-piano-secondo.jpg` | Planimetria del piano secondo — **già reale** | scansione A4 | 5:7 verticale |
| `og-image.jpg` | Anteprima quando il link è condiviso su WhatsApp/Facebook | 1200 × 630 | 1.91:1 |

Note pratiche:

* **`og-image.jpg` è già pronta e utilizzabile** (non è un placeholder): grafica
  navy/oro con nome, indirizzo e claim. Sostituiscila solo se vuoi una foto.
* **Le due planimetrie dei piani sono reali**, non placeholder. `generate-placeholders.py`
  le lascia intenzionalmente fuori dalla sua lista, quindi rilanciarlo non le
  sovrascrive.
* Le planimetrie sono mostrate con `object-fit: contain` su sfondo bianco: una
  planimetria non va mai ritagliata, quindi se le proporzioni non coincidono
  esattamente con 5:7 compaiono due sottili bande bianche invece di un taglio.
  Puoi quindi caricarle in qualsiasi formato senza rompere nulla.
* Le planimetrie possono essere anche disegni a mano scansionati o esportazioni
  da Canva: vanno bene sia `.jpg` sia `.png` (in quel caso rinomina il file in
  `.jpg` **oppure** aggiorna il `src` corrispondente in `index.html`).
* Comprimi le immagini prima di caricarle: puntare a **150–250 KB per immagine**.
  Strumenti gratuiti: [squoosh.app](https://squoosh.app) o [tinypng.com](https://tinypng.com).
* Dopo aver sostituito un'immagine, **aggiorna il testo `alt`** nell'`index.html`
  se il contenuto della foto è diverso da quello descritto: l'`alt` conta per la SEO.
  Cerca il commento `<!-- PLACEHOLDER: ... -->` che precede ogni immagine.
* Per rigenerare i placeholder (se ne servono altri o con altre etichette):
  `python3 tools/generate-placeholders.py`.

### Dopo ogni sostituzione: rigenera le varianti

Il sito non serve i JPEG che hai appena sostituito: serve versioni **AVIF e
WebP** più leggere, generate in più larghezze, e lascia scegliere al browser
quella giusta. Sono in `assets/img/opt/` e vanno rigenerate a ogni cambio.

Una volta sola, per installare le dipendenze:

```bash
python3 -m pip install -r tools/requirements.txt
```

Poi, ogni volta che sostituisci una o più immagini:

```bash
python3 tools/build-images.py
```

Lo script:

* genera AVIF e WebP a 480, 960, 1440 px (mai più grandi dell'originale);
* segnala se una foto sostituita ha **proporzioni diverse** da quelle attese —
  in quel caso vanno aggiornati `width` e `height` nel tag `<img>` corrispondente
  in `index.html`, altrimenti il layout "salta" durante il caricamento;
* scrive `assets/img/opt/manifest.json` con l'impronta di ogni sorgente.

**Se te ne dimentichi il sito mostra ancora le foto vecchie, in silenzio.**
Per questo il deploy su GitHub Actions esegue `build-images.py --check` e
**si ferma con un errore** se le varianti non sono allineate ai sorgenti.
Puoi lanciare tu stesso il controllo in qualsiasi momento:

```bash
python3 tools/build-images.py --check
```

L'HTML non va mai toccato: i tag `<picture>` puntano a nomi di file fissi.
Fanno eccezione solo `og-image.jpg` (le anteprime social vogliono un JPEG) e la
lightbox delle planimetrie, che apre l'originale `.jpg` a tutta risoluzione.

---

## 4. Sostituire il logo

Oggi il logo è un **placeholder tipografico**: un quadrato bianco con la "R" e il
bordo oro, coerente con la locandina. Compare in due punti (header e footer).

Per usare il logo definitivo:

1. Metti il file in `assets/img/logo-residence-roma.svg` (SVG preferibile; in
   alternativa PNG trasparente da almeno 512 px).
2. In `index.html` cerca `brand__mark` (2 occorrenze) e sostituisci

   ```html
   <span class="brand__mark" aria-hidden="true">R</span>
   ```

   con

   ```html
   <img class="brand__mark" src="assets/img/logo-residence-roma.svg"
        width="38" height="38" alt="" aria-hidden="true">
   ```

3. Sostituisci anche `assets/img/favicon.svg` (icona della scheda del browser) e
   `assets/img/apple-touch-icon.png` (180 × 180, icona su iPhone/iPad).

---

## 5. Cambiare il dominio (importante per la SEO)

Oggi tutti gli URL assoluti puntano al placeholder
`https://ciock.github.io/RentingHouseSite/`.

Quando il dominio definitivo è confermato, sostituiscilo in **tre file**
(cerca `TODO DOMINIO` nei commenti):

| File | Cosa aggiornare |
|---|---|
| `index.html` | `<link rel="canonical">`, tutti i tag `og:` e `twitter:`, i tre URL nel blocco JSON-LD |
| `sitemap.xml` | il tag `<loc>`, gli URL delle immagini e la data in `<lastmod>` |
| `robots.txt` | la riga `Sitemap:` |

Da terminale, nella cartella del progetto:

```bash
grep -rl "ciock.github.io/RentingHouseSite" . --exclude-dir=.git
```

---

## 6. Cambiare contatti, numero WhatsApp e testi

* **Numero WhatsApp**: cerca `393929715552` in `index.html` (formato internazionale
  senza `+` e senza spazi). Compare in 7 link `https://wa.me/...`.
* **Messaggio precompilato di WhatsApp**: è la parte dopo `?text=`, codificata in
  URL (`%20` = spazio). Ogni pulsante ha un messaggio diverso (visita, camera
  singola, camera doppia, informazioni generiche).
* **Telefono cliccabile**: cerca `tel:+393929715552`.
* **Email**: cerca `ResidenceRoma.Piacenza@gmail.com` (link `mailto:`, footer e JSON-LD).
* **Social**: nel footer i due link Instagram/Facebook hanno `href="#"`.
  Inserisci gli URL reali, oppure elimina l'intero blocco `<div class="footer__col">`
  che contiene `footer__social`.
* **Titolo rotante dell'hero**: la riga in oro cicla fra le distanze. Le frasi
  stanno nell'attributo `data-phrases` dello `<span class="rotator">` in
  `index.html`, separate da `|`. Per aggiungerne, toglierne o riscriverne una
  basta modificare quell'attributo — il JavaScript non va toccato.
  Due regole: la **prima frase** deve restare identica al testo scritto dentro
  `<span class="hl">` subito sotto (è quella che vedono Google e chi ha il
  JavaScript disattivato), e conviene tenere le frasi di **lunghezza simile**,
  perché lo spazio riservato è quello della frase più lunga. Velocità e durata
  della dissolvenza sono `ROT_HOLD` e `ROT_FADE` in `assets/js/main.js`.
* **Prezzi**: per scelta non sono pubblicati sul sito; la nota in fondo alla
  sezione contatti dice che vengono comunicati al primo contatto.

---

## 7. Aggiungere un form di contatto reale

Il sito, per scelta, usa solo **WhatsApp, telefono ed email**: sono i canali con
il tasso di risposta più alto per un pubblico di studenti e non richiedono nulla
lato server.

Se in futuro serve un form, un sito statico non può inviare email da solo: serve
un servizio esterno che riceve l'invio e lo gira per email. Le tre opzioni più
semplici (tutte con piano gratuito):

**A. Formspree** — funziona ovunque, anche su GitHub Pages.

1. Registrati su [formspree.io](https://formspree.io) e crea un form: ottieni un
   endpoint tipo `https://formspree.io/f/xxxxxxx`.
2. Aggiungi nella sezione `#contatti` di `index.html`:

   ```html
   <form action="https://formspree.io/f/xxxxxxx" method="POST">
     <label for="nome">Nome</label>
     <input id="nome" name="nome" type="text" required>

     <label for="email">Email</label>
     <input id="email" name="email" type="email" required>

     <label for="messaggio">Messaggio</label>
     <textarea id="messaggio" name="messaggio" rows="4" required></textarea>

     <!-- anti-spam: campo nascosto che gli umani non compilano -->
     <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" hidden>

     <button class="btn btn--gold" type="submit">Invia richiesta</button>
   </form>
   ```

3. La validazione di base è già nativa del browser grazie a `required` e
   `type="email"`: non serve JavaScript aggiuntivo.

**B. Netlify Forms** — solo se pubblichi su Netlify: aggiungi `netlify` e
`name="contatti"` al tag `<form>` e la raccolta è automatica, zero configurazione.

**C. Web3Forms / Getform** — alternative equivalenti a Formspree.

In tutti i casi, verifica che l'email di destinazione sia
`ResidenceRoma.Piacenza@gmail.com` e fai un invio di prova.

---

## 8. Pubblicare il sito online

Il sito è completamente statico: qualsiasi hosting va bene, anche gratuito.

### GitHub Pages (scelta attuale)

```bash
git init
git add .
git commit -m "Sito Residence Roma Piacenza"
git branch -M main
git remote add origin https://github.com/Ciock/RentingHouseSite.git
git push -u origin main
```

Poi su GitHub: **Settings → Pages → Source: `Deploy from a branch` → Branch:
`main` / `root` → Save**. Dopo 1–2 minuti il sito è online su
`https://ciock.github.io/RentingHouseSite/`.

Il file `.nojekyll` è già presente e serve a far servire i file così come sono.

> Ogni `git push` aggiorna il sito. Dopo un aggiornamento, se non vedi le
> modifiche, forza il ricaricamento con `Cmd/Ctrl + Shift + R`.

### Netlify

Trascina la cartella del progetto su [app.netlify.com/drop](https://app.netlify.com/drop):
il sito è online in pochi secondi. In alternativa collega il repository GitHub e
Netlify ripubblica a ogni push (build command vuoto, publish directory `.`).

### Vercel

[vercel.com/new](https://vercel.com/new) → importa il repository → framework
preset **Other** → Deploy.

### Dominio personalizzato

Quando il cliente conferma il dominio (es. `residenceromapiacenza.it`):

1. Collegalo dal pannello dell'hosting (GitHub Pages: *Settings → Pages → Custom domain*).
2. Attiva HTTPS (su tutte e tre le piattaforme è un flag, gratuito).
3. **Aggiorna gli URL come descritto al punto 5.**

---

## 9. Checklist SEO dopo la pubblicazione

Cose già fatte nel codice:

- [x] HTML semantico, una sola `<h1>`, gerarchia `h2`/`h3` corretta
- [x] `<title>` e meta description ottimizzati su "camere studenti Piacenza"
- [x] Open Graph + Twitter Card con immagine 1200 × 630
- [x] Dati strutturati Schema.org `LodgingBusiness` + `LocalBusiness`, con le due
      tipologie di camera come `Accommodation`
- [x] `alt` descrittivi su tutte le immagini
- [x] `sitemap.xml`, `robots.txt`, `canonical`
- [x] Anchor link puliti (`#camere`, `#servizi`, `#planimetrie`, `#posizione`, `#contatti`)
- [x] Testi presenti nell'HTML, non generati via JavaScript

Cose da fare tu, dopo il primo deploy:

- [ ] Sostituire il dominio placeholder (punto 5)
- [ ] Verificare il sito su [Google Search Console](https://search.google.com/search-console)
      e inviare la `sitemap.xml`
- [ ] Creare/rivendicare la scheda **Google Business Profile** del residence:
      per una struttura locale porta più contatti del sito stesso
- [ ] Aggiungere il **CAP** all'indirizzo (in `index.html`, dentro il blocco JSON-LD,
      aggiungi `"postalCode": "291xx"` in `address`) — non l'ho inserito per non
      indovinare un dato non presente nella locandina
- [ ] Facoltativo: aggiungere le **coordinate geografiche** al JSON-LD, prendendole
      da Google Maps (tasto destro sul punto esatto → coordinate):

  ```json
  "geo": { "@type": "GeoCoordinates", "latitude": 45.0xxx, "longitude": 9.7xxxx }
  ```

- [ ] Testare l'anteprima social su
      [opengraph.xyz](https://www.opengraph.xyz) e i dati strutturati su
      [validator.schema.org](https://validator.schema.org)

---

## 10. Note tecniche e performance

Il peso del primo caricamento è di circa **35 KB** (HTML + CSS + JS compressi,
più l'immagine hero in AVIF). Scelte fatte per tenerlo basso:

* **Zero librerie esterne.** Slider, lightbox, menu e animazioni sono ~7 KB di
  JavaScript scritto a mano. Niente jQuery, niente framework.
* **Icone SVG inline** in un unico sprite dentro l'HTML: nessuna richiesta di rete
  aggiuntiva e nessun font di icone da scaricare.
* **Mappa caricata solo al click.** L'embed di Google Maps pesa oltre 1 MB: la
  sezione mostra un'anteprima leggera e carica l'`iframe` solo quando l'utente
  preme "Mostra la mappa". Chi ha JavaScript disattivato vede comunque la mappa
  (fallback `<noscript>`).
* **Font Google non bloccante.** Il testo è subito leggibile con il font di
  sistema e Manrope subentra appena disponibile. Per azzerare anche questa
  richiesta esterna, rimuovi i tre `<link>` dei font in `index.html`: il sito
  resta identico nella struttura, con il font di sistema.
* **Immagini in AVIF/WebP responsive.** Ogni foto esiste in AVIF e WebP a più
  larghezze; i tag `<picture>` fanno scegliere al browser il formato migliore che
  supporta e la larghezza più vicina a quella che gli serve davvero. Il JPEG resta
  solo come rete di sicurezza per browser molto vecchi. Nessun browser moderno
  lo scarica: verificato, zero richieste `.jpg` a caricamento completo.

  | Scenario | Immagini scaricate | Prima (solo JPEG) | |
  |---|---|---|---|
  | Mobile 375 px @2x | 255 KB | 2398 KB | **-89%** |
  | Desktop 1440 px @1x | 117 KB | 2398 KB | **-95%** |
  | Desktop 1440 px @2x | 278 KB | 2398 KB | **-88%** |

  Il divario si è allargato con le planimetrie reali: sono scansioni da 880 KB
  l'una, e la card ne usa una versione da 16 KB.

  Sulla sola immagine hero — l'unica sopra la piega, quindi l'unica che pesa sul
  tempo di apertura — si passa da **106 KB a 16 KB su mobile (-85%)**.

* **La lightbox apre la variante ottimizzata**, non lo scan originale: una
  planimetria ingrandita costa **175 KB invece di 880 KB**. Se il file
  ottimizzato mancasse, il JavaScript ripiega da solo sul JPEG di partenza.

* **Immagini**: `width`/`height` dichiarati su tutte (niente sfarfallio del layout
  durante il caricamento), `loading="lazy"` su tutte tranne l'hero, che è invece
  in `preload` responsive (`imagesrcset`) con `fetchpriority="high"` perché è
  l'elemento più grande della prima schermata.
* **Animazioni**: usano `IntersectionObserver` e si disattivano da sole se il
  sistema operativo ha attivo "riduci movimento". Senza JavaScript i contenuti
  restano visibili.
* **Accessibilità**: skip-link, `aria-expanded` sul menu, focus visibile, `aria-label`
  sui link solo-icona, lightbox in `<dialog>` nativo (Esc, click sullo sfondo e
  ripristino del focus funzionano).

### Breakpoint responsive

| Larghezza | Layout |
|---|---|
| < 600 px | tutto su una colonna, menu hamburger, pulsante WhatsApp flottante |
| ≥ 600 px | servizi e footer su 2 colonne |
| ≥ 700 px | galleria su 3 colonne, planimetrie su 2 |
| ≥ 860 px | camere affiancate su 2 colonne |
| ≥ 900 px | menu orizzontale, contatti su 3 colonne |
| ≥ 1024 px | hero su 2 colonne, servizi e planimetrie su 3, mappa affiancata |
| ≥ 1280 px | servizi su 4 colonne |

Testato a 375, 768, 1024 e 1440 px.

### Browser supportati

Chrome, Edge, Firefox e Safari aggiornati (desktop e mobile). Su browser molto
datati senza `<dialog>`, il click su una planimetria apre l'immagine in una nuova
scheda invece della lightbox.
