/* =============================================================================
   Residence Roma Piacenza — JS vanilla, nessuna dipendenza.
   1. Header sticky   2. Titolo hero rotante   3. Menu mobile   4. Scrollspy
   5. Micro-animazioni   6. Lightbox   7. Mappa on-demand   8. Anno nel footer
   ========================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DESKTOP = window.matchMedia('(min-width: 56.25em)');

  /* ---------------------------------------------------------------- 1. Header */
  var header = document.getElementById('site-header');
  if (header) {
    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        header.classList.toggle('is-stuck', window.scrollY > 8);
        ticking = false;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ------------------------------------------------- 2. Titolo hero rotante */
  var rotator = document.getElementById('hero-rotator');

  if (rotator && !reduceMotion) {
    var rotInner = rotator.querySelector('.rotator__inner');
    var rotText = rotator.querySelector('.hl');
    var phrases = (rotator.getAttribute('data-phrases') || '')
      .split('|')
      .map(function (t) { return t.trim(); })
      .filter(Boolean);

    if (rotInner && rotText && phrases.length > 1) {
      var ROT_HOLD = 3200;   // quanto resta ferma ogni frase
      var ROT_FADE = 300;    // deve coincidere con la transition in style.css
      var rotIndex = 0;
      var rotTimer = null;
      var rotResize;

      // Riserva l'altezza della frase più alta: senza questo ogni cambio di
      // testo sposterebbe verso il basso tutto il contenuto della pagina.
      function reserveHeight() {
        var tallest = 0;
        rotator.style.minHeight = '';
        for (var i = 0; i < phrases.length; i++) {
          rotText.textContent = phrases[i];
          tallest = Math.max(tallest, rotator.offsetHeight);
        }
        rotText.textContent = phrases[rotIndex];
        rotator.style.minHeight = tallest + 'px';
      }

      function showNext() {
        rotInner.classList.add('is-out');
        window.setTimeout(function () {
          rotIndex = (rotIndex + 1) % phrases.length;
          rotText.textContent = phrases[rotIndex];
          rotInner.classList.remove('is-out');
        }, ROT_FADE);
      }

      function rotPlay() {
        if (rotTimer) return;
        rotTimer = window.setInterval(showNext, ROT_HOLD);
      }
      function rotPause() {
        window.clearInterval(rotTimer);
        rotTimer = null;
      }

      reserveHeight();
      // Con il font di sistema le altezze sono diverse: rimisura quando
      // Manrope è pronto.
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(function () { reserveHeight(); });
      }

      window.addEventListener('resize', function () {
        window.clearTimeout(rotResize);
        rotResize = window.setTimeout(reserveHeight, 150);
      }, { passive: true });

      // Si ferma quando la scheda non è visibile e quando il mouse o il focus
      // sono sul titolo, per lasciare il tempo di leggere.
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) rotPause(); else rotPlay();
      });

      var heroTitle = document.getElementById('hero-title');
      if (heroTitle) {
        heroTitle.addEventListener('mouseenter', rotPause);
        heroTitle.addEventListener('mouseleave', rotPlay);
        heroTitle.addEventListener('focusin', rotPause);
        heroTitle.addEventListener('focusout', rotPlay);
      }

      rotPlay();
    }
  }

  /* ----------------------------------------------------------- 3. Menu mobile */
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('primary-nav');

  function setMenu(open) {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Chiudi il menu di navigazione' : 'Apri il menu di navigazione');
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-open', open);
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });

    // Chiudi dopo il click su una voce (lo scroll all'ancora resta nativo)
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        toggle.focus();
      }
    });

    // Click fuori dal pannello
    document.addEventListener('click', function (e) {
      if (toggle.getAttribute('aria-expanded') !== 'true') return;
      if (nav.contains(e.target) || toggle.contains(e.target)) return;
      setMenu(false);
    });

    // Tornando a desktop il pannello mobile non deve restare "aperto"
    var syncViewport = function (e) { if (e.matches) setMenu(false); };
    if (DESKTOP.addEventListener) DESKTOP.addEventListener('change', syncViewport);
    else if (DESKTOP.addListener) DESKTOP.addListener(syncViewport);
  }

  /* ------------------------------------------------------------ 4. Scrollspy */
  var navLinks = nav ? Array.prototype.slice.call(nav.querySelectorAll('.nav__list a[href^="#"]')) : [];
  var sections = navLinks
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    var visible = Object.create(null);

    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });

      var bestId = null, bestRatio = 0;
      sections.forEach(function (s) {
        if ((visible[s.id] || 0) > bestRatio) { bestRatio = visible[s.id]; bestId = s.id; }
      });

      navLinks.forEach(function (a) {
        if (bestId && a.getAttribute('href') === '#' + bestId) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    }, { rootMargin: '-30% 0px -45% 0px', threshold: [0, .25, .5, .75, 1] });

    sections.forEach(function (s) { spy.observe(s); });
  }

  /* --------------------------------------------------- 5. Micro-animazioni */
  var revealables = document.querySelectorAll('.reveal');

  if (reduceMotion || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .12 });

    Array.prototype.forEach.call(revealables, function (el, i) {
      // scaglionamento leggero fra elementi della stessa griglia
      el.style.transitionDelay = (i % 4) * 70 + 'ms';
      io.observe(el);
    });
  }

  /* ------------------------------------------------------------ 6. Lightbox */
  var dialog = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightbox-img');
  var lbCap = document.getElementById('lightbox-cap');
  var lbClose = document.getElementById('lightbox-close');
  var lastFocused = null;

  function openLightbox(trigger) {
    var src = trigger.getAttribute('data-src');
    var caption = trigger.getAttribute('data-caption') || '';
    var thumb = trigger.querySelector('img');
    if (!src) return;

    // Senza <dialog> (browser molto datati) apriamo l'immagine a piena pagina
    if (!dialog || typeof dialog.showModal !== 'function') {
      window.open(src, '_blank', 'noopener');
      return;
    }

    lastFocused = document.activeElement;

    // La lightbox apre la variante ottimizzata (molto più leggera dello
    // scan originale). Se manca o il formato non è supportato, ripiega
    // sul JPEG di partenza, che c'è sempre.
    var fallback = trigger.getAttribute('data-src-fallback');
    lbImg.onerror = function () {
      lbImg.onerror = null;
      if (fallback) lbImg.src = fallback;
    };

    lbImg.src = src;
    lbImg.alt = thumb ? thumb.alt : caption;
    lbCap.textContent = caption;
    dialog.showModal();
  }

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-lightbox]');
    if (trigger) { e.preventDefault(); openLightbox(trigger); }
  });

  function closeLightbox() {
    if (!dialog) return;
    if (dialog.open) dialog.close();
    lbImg.removeAttribute('src');
    lbImg.alt = '';
    if (lastFocused && lastFocused.focus) lastFocused.focus();
    lastFocused = null;
  }

  if (dialog) {
    if (lbClose) lbClose.addEventListener('click', closeLightbox);

    // Click sullo sfondo scuro
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog) closeLightbox();
    });

    // Esc: 'cancel' precede la chiusura nativa, 'close' copre gli altri casi.
    dialog.addEventListener('cancel', function () {
      window.setTimeout(closeLightbox, 0);
    });
    dialog.addEventListener('close', closeLightbox);
  }

  /* -------------------------------------------------------- 7. Mappa lazy */
  var mapBox = document.getElementById('map');
  var mapBtn = document.getElementById('map-load');

  if (mapBox && mapBtn) {
    mapBtn.addEventListener('click', function () {
      var src = mapBox.getAttribute('data-map-src');
      if (!src) return;
      var frame = document.createElement('iframe');
      frame.className = 'map__frame';
      frame.src = src;
      frame.title = 'Mappa di Via Roma 324, Piacenza';
      frame.loading = 'lazy';
      frame.setAttribute('referrerpolicy', 'no-referrer-when-downgrade');
      frame.setAttribute('allowfullscreen', '');
      mapBox.replaceChildren(frame);
    });
  }

  /* ------------------------------------------------------- 8. Anno footer */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
