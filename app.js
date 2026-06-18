/* Turar — site behavior (theme, mobile nav, header, reveal, lightbox).
   Language is handled at build time (one pre-rendered page per language); the
   header language switch is plain links, so no client-side i18n lives here. */
(function () {
  var root = document.documentElement;

  /* ---------- theme (ivory default, night toggle; persisted) ---------- */
  function setThemeGlyph() {
    var b = document.getElementById("theme-toggle");
    if (b) b.textContent = root.dataset.theme === "ivory" ? "☾" : "☀";
  }

  function init() {
    /* theme toggle */
    setThemeGlyph();
    var themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) themeBtn.addEventListener("click", function () {
      root.dataset.theme = root.dataset.theme === "ivory" ? "night" : "ivory";
      try { localStorage.setItem("turar-theme", root.dataset.theme); } catch (e) {}
      setThemeGlyph();
    });

    /* mobile nav */
    var navToggle = document.getElementById("nav-toggle");
    var mainNav = document.getElementById("main-nav");
    if (navToggle && mainNav) {
      navToggle.addEventListener("click", function () {
        var open = mainNav.classList.toggle("open");
        navToggle.setAttribute("aria-expanded", open);
      });
      mainNav.addEventListener("click", function (e) {
        if (e.target.tagName === "A") { mainNav.classList.remove("open"); navToggle.setAttribute("aria-expanded", "false"); }
      });
    }

    /* header scroll state */
    var header = document.getElementById("header");
    if (header) {
      var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 24); };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    /* reveal on scroll (visible by default; hidden then revealed) */
    if ("IntersectionObserver" in window && matchMedia("(prefers-reduced-motion: no-preference)").matches) {
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.remove("pre"); io.unobserve(en.target); } });
        }, { threshold: 0.12 });
        document.querySelectorAll(".reveal").forEach(function (el) {
          if (el.getBoundingClientRect().top > window.innerHeight * 0.95) { el.classList.add("pre"); io.observe(el); }
        });
      }); });
    }

    /* lightbox (only if present) */
    initLightbox();
  }

  function initLightbox() {
    var lightbox = document.getElementById("lightbox");
    var shots = Array.prototype.slice.call(document.querySelectorAll(".shot"));
    if (!lightbox || !shots.length) return;
    var WEBP_OK = (function () {
      try { var c = document.createElement("canvas"); return !!(c.getContext && c.getContext("2d")) && c.toDataURL("image/webp").indexOf("data:image/webp") === 0; }
      catch (e) { return false; }
    })();
    function bestSrc(u) { return WEBP_OK ? u.replace(/\.jpe?g$/i, ".webp") : u; }
    var lbImg = document.getElementById("lb-img");
    var lbCap = document.getElementById("lb-cap");
    var lbClose = document.getElementById("lb-close");
    var lbPrev = document.getElementById("lb-prev");
    var lbNext = document.getElementById("lb-next");
    var focusable = [lbPrev, lbNext, lbClose];
    var current = 0, lastFocused = null, isOpen = false;

    function hashFor(i) { return "#work-" + (i + 1); }
    function indexFromHash() {
      var m = /^#work-(\d+)$/.exec(location.hash);
      if (!m) return -1;
      var i = parseInt(m[1], 10) - 1;
      return (i >= 0 && i < shots.length) ? i : -1;
    }
    function setHash(i, replace) {
      try { history[replace ? "replaceState" : "pushState"]({ lb: i }, "", hashFor(i)); } catch (e) {}
    }

    function render() {
      var el = shots[current];
      var work = el.closest(".work");
      var img = el.querySelector("img");
      var jpg = el.getAttribute("href") || img.src;
      var full = bestSrc(jpg);
      var title = work ? work.querySelector(".work-title").textContent : "";
      var medium = work ? work.querySelector(".work-medium").textContent : "";
      lbImg.classList.add("is-loading");
      var pre = new Image();
      pre.onload = function () { lbImg.src = full; lbImg.alt = img.alt; lbImg.classList.remove("is-loading"); };
      pre.onerror = function () { if (full !== jpg) { lbImg.src = jpg; lbImg.alt = img.alt; lbImg.classList.remove("is-loading"); } };
      pre.src = full;
      lbCap.innerHTML = "<em>" + title + "</em>" + medium;
      [current - 1, current + 1].forEach(function (n) {
        var f = shots[(n + shots.length) % shots.length].getAttribute("href"); if (f) { var im = new Image(); im.src = bestSrc(f); }
      });
    }
    function open(i, push) {
      current = i; lastFocused = shots[i]; render();
      lightbox.classList.add("is-open"); document.body.style.overflow = "hidden"; isOpen = true; lbClose.focus();
      if (push !== false) setHash(i, false);
    }
    function close(viaPop) {
      lightbox.classList.remove("is-open"); document.body.style.overflow = ""; isOpen = false;
      if (lastFocused) lastFocused.focus();
      if (!viaPop && indexFromHash() !== -1) { try { history.back(); } catch (e) {} }
    }
    function nav(d) { current = (current + d + shots.length) % shots.length; render(); setHash(current, true); }

    shots.forEach(function (shot, i) {
      shot.addEventListener("click", function (e) { e.preventDefault(); open(i); });
      var vl = shot.parentNode.querySelector(".view-link");
      if (vl) vl.addEventListener("click", function () { open(i); });
    });
    lbClose.addEventListener("click", function () { close(); });
    lbPrev.addEventListener("click", function () { nav(-1); });
    lbNext.addEventListener("click", function () { nav(1); });
    lightbox.addEventListener("click", function (e) { if (e.target === lightbox || e.target.classList.contains("lightbox__figure")) close(); });
    document.addEventListener("keydown", function (e) {
      if (!isOpen) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft") nav(-1);
      else if (e.key === "ArrowRight") nav(1);
      else if (e.key === "Tab") {
        var idx = focusable.indexOf(document.activeElement);
        if (e.shiftKey && idx <= 0) { e.preventDefault(); focusable[focusable.length - 1].focus(); }
        else if (!e.shiftKey && idx === focusable.length - 1) { e.preventDefault(); focusable[0].focus(); }
        else if (idx === -1) { e.preventDefault(); focusable[0].focus(); }
      }
    });

    /* touch swipe (mobile) */
    var x0 = null, y0 = null;
    lightbox.addEventListener("touchstart", function (e) { var t = e.changedTouches[0]; x0 = t.clientX; y0 = t.clientY; }, { passive: true });
    lightbox.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0;
      x0 = y0 = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) nav(dx < 0 ? 1 : -1);
    }, { passive: true });

    /* deep-linking: shareable #work-N, browser back closes/navigates */
    window.addEventListener("popstate", function () {
      var i = indexFromHash();
      if (i !== -1) { if (!isOpen) open(i, false); else { current = i; render(); } }
      else if (isOpen) close(true);
    });
    var initial = indexFromHash();
    if (initial !== -1) {
      try { history.replaceState(null, "", location.pathname + location.search); } catch (e) {}
      open(initial);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
