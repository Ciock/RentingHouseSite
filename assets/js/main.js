/* =============================================================================
   Residence Roma Piacenza — JS vanilla, nessuna dipendenza.
   1. Header sticky   2. Menu mobile   3. Scrollspy   4. Micro-animazioni
   5. Lightbox        6. Mappa on-demand              7. Anno nel footer
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

  /* ----------------------------------------------------------- 2. Menu mobile */
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

  /* ------------------------------------------------------------ 3. Scrollspy */
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

  /* --------------------------------------------------- 4. Micro-animazioni */
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

  /* ------------------------------------------------------------ 5. Lightbox */
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

  /* -------------------------------------------------------- 6. Mappa lazy */
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

  /* ------------------------------------------------------- 7. Anno footer */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
