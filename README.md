# Turar — Sacred Embroidery of Kyrgyzstan

A gallery website for textile artist **Turar Turganalieva**, member of the Union of
Artists of the Kyrgyz Republic. Hand-embroidered ornament — drawn in soap on cloth,
finished in silk. The site is a portfolio/gallery (no e-commerce): collectors inquire
for a price by email.

Built to the Claude Design handoff: **Cormorant Garamond + Manrope**, an ivory
gallery-white palette with a cinnabar accent, a night theme, and a quiet abstract
*tumar* (lozenge) motif.

## Pages

- **`index.html`** — hero, quote band, the Selected Works gallery (click any piece for
  a full-screen lightbox), an artist teaser, and an inquiry section.
- **`about.html`** — the artist's story, written from her podcast interview (two lives,
  eight years at the window, the practice, a language of signs, recognition, the atelier).

## Features

- **Four languages** — EN / RU / ES / FR, switchable in the header (choice persists).
- **Two themes** — ivory (default) and night, toggle in the header (persists).
- **Responsive** — masonry gallery collapses to one column; mobile nav menu.
- **Optimized images** — every photo ships as WebP + JPEG via `<picture>` (WebP first,
  JPEG fallback, ~23% smaller). The gallery loads the `photos/web/` grid set; the lightbox
  loads larger versions on demand.
- **SEO / social** — canonical URLs, Open Graph & Twitter cards with absolute image URLs,
  `Person`/`WebSite` JSON-LD, plus `robots.txt` and `sitemap.xml`.
- **Accessible** — WCAG-AA text contrast, a keyboard- and focus-trapped lightbox, an OS
  dark-mode default (`prefers-color-scheme`), and reduced-motion awareness. With JavaScript
  off, each gallery piece is a real link to its full-size image.

## Run locally

No build step — it's static HTML/CSS/JS. Either open `index.html` directly, or serve it:

```bash
npx serve .
# then open http://localhost:3000
```

## Project structure

```
index.html, about.html   pages
styles.css               all styles (design tokens, themes, layout, lightbox)
app.js                   translations (EN/RU/ES/FR) + behavior (theme, i18n, lightbox)
favicon.svg              tumar-lozenge mark
robots.txt, sitemap.xml  crawl directives (point to the production domain)
optimize_images.py       regenerate photos/web/ from originals (needs Pillow)
photos/web/              optimized images (.jpg + .webp) used by the site (committed)
photos/web/large/        larger versions (.jpg + .webp) for the lightbox
```

> The original high-resolution photographs and `Turart Photos.zip` are **not** committed
> (they're large and live on the artist's machine). Run `python optimize_images.py` after
> dropping new originals into `photos/Turarts/` to regenerate the optimized set.

## To finish before launch

- **Domain** — canonical / Open Graph / sitemap / robots URLs assume `https://turar.art`.
  If the real domain differs, update it in `index.html`, `about.html`, `sitemap.xml` and
  `robots.txt` (absolute URLs are required for social link previews to render).
- **Email** — the inquiry button points to a placeholder `hello@turar.art`.
- **Instagram** — link is a placeholder.
- **Work titles** — the gallery uses descriptive placeholder titles; the artist's real
  titles (e.g. *Neural Network, Chalice of Love, Scarab, Roots of the Kin*) can be mapped
  to the corresponding photos.
