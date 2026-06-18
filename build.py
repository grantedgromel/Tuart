#!/usr/bin/env python3
"""Static-site generator for the Turar gallery.

Reads the English templates in templates/ plus the translations in i18n.json and
writes a fully pre-rendered page per language, so every language is crawlable and
works without JavaScript:

    /index.html          /about.html          (en, x-default)
    /ru/index.html       /ru/about.html
    /es/index.html       /es/about.html
    /fr/index.html       /fr/about.html

It also bakes in per-page <title>/description, canonical + hreflang alternates,
Open Graph locale tags, language-aware nav links and a link-based language
switcher, and regenerates sitemap.xml.

Source of truth: edit templates/*.html and i18n.json, then run `python build.py`
and commit the result. Asset files (styles.css, app.js, photos/, favicon.svg,
robots.txt) are static and served from the site root.

The production origin defaults to the turar.art placeholder; override with
SITE_URL=https://example.com when a real domain is connected.

    python build.py
"""
import json
import os
from bs4 import BeautifulSoup, NavigableString

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE_URL", "https://turar.art").rstrip("/")
LANGS = ["en", "ru", "es", "fr"]
LOCALES = {"en": "en_US", "ru": "ru_RU", "es": "es_ES", "fr": "fr_FR"}
# data-i18n key -> internal link role (so nav/CTA hrefs become language-aware).
ROLE = {
    "nav_works": "works", "nav_artist": "about", "nav_inquire": "inquire",
    "hero_cta": "works", "artist_link": "about",
    "ab_cta_works": "works", "ab_cta_inq": "inquire",
}
PAGES = {"home": "index.html", "about": "about.html"}


def path(lang, page):
    """Root-relative URL of a page in a language (e.g. /ru/about.html)."""
    prefix = "" if lang == "en" else f"/{lang}"
    return f"{prefix}/" if page == "home" else f"{prefix}/{PAGES[page]}"


def abs_url(lang, page):
    return SITE + path(lang, page)


def role_href(role, lang):
    b = "" if lang == "en" else f"/{lang}"
    return {"home": f"{b}/", "works": f"{b}/#works",
            "about": f"{b}/about.html", "inquire": f"{b}/#inquire"}[role]


def absolutize_assets(soup):
    """Relative asset paths -> root-absolute, so subdirectory pages resolve them."""
    for sel, attr in (('link[href="styles.css"]', "href"),
                      ('link[href="favicon.svg"]', "href"),
                      ('script[src="app.js"]', "src")):
        el = soup.select_one(sel)
        if el:
            el[attr] = "/" + el[attr]
    for el in soup.select("img[src]"):
        if el["src"].startswith("photos/"):
            el["src"] = "/" + el["src"]
    for el in soup.select("source[srcset]"):
        if el["srcset"].startswith("photos/"):
            el["srcset"] = "/" + el["srcset"]
    for el in soup.select("a.shot[href]"):
        if el["href"].startswith("photos/"):
            el["href"] = "/" + el["href"]


def set_meta(soup, selector, value):
    el = soup.select_one(selector)
    if el:
        el["content"] = value


def render(page, lang, T):
    with open(os.path.join(BASE, "templates", PAGES[page]), encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    soup.html["lang"] = lang
    absolutize_assets(soup)

    # text + aria translations
    for el in soup.select("[data-i18n]"):
        v = T.get(el["data-i18n"])
        if v is not None:
            el.clear()
            el.append(NavigableString(v))
    for el in soup.select("[data-i18n-aria]"):
        v = T.get(el["data-i18n-aria"])
        if v is not None:
            el["aria-label"] = v

    # language-aware internal links
    wm = soup.select_one("a.wordmark")
    if wm:
        wm["href"] = role_href("home", lang)
    for a in soup.select("a[data-i18n]"):
        role = ROLE.get(a.get("data-i18n"))
        if role:
            a["href"] = role_href(role, lang)

    # head: title / description / canonical / OG / Twitter
    title, desc = T[f"meta_title_{page}"], T[f"meta_desc_{page}"]
    if soup.title:
        soup.title.string = title
    set_meta(soup, 'meta[name="description"]', desc)
    can = soup.select_one('link[rel="canonical"]')
    if can:
        can["href"] = abs_url(lang, page)
    set_meta(soup, 'meta[property="og:url"]', abs_url(lang, page))
    set_meta(soup, 'meta[property="og:title"]', title)
    set_meta(soup, 'meta[property="og:description"]', desc)
    set_meta(soup, 'meta[name="twitter:title"]', title)
    set_meta(soup, 'meta[name="twitter:description"]', desc)
    og_locale = soup.select_one('meta[property="og:locale"]')
    if og_locale:
        og_locale["content"] = LOCALES[lang]

    # og:locale:alternate — rebuild for the other languages
    for m in soup.select('meta[property="og:locale:alternate"]'):
        m.decompose()
    anchor = og_locale
    for L in LANGS:
        if L == lang or anchor is None:
            continue
        m = soup.new_tag("meta")
        m["property"] = "og:locale:alternate"
        m["content"] = LOCALES[L]
        anchor.insert_after(m)
        anchor = m

    # hreflang alternates (+ x-default -> English)
    for l in soup.select('link[rel="alternate"][hreflang]'):
        l.decompose()
    ref = can
    pairs = [(L, L) for L in LANGS] + [("x-default", "en")]
    for hreflang, L in pairs:
        if ref is None:
            break
        lk = soup.new_tag("link")
        lk["rel"] = "alternate"
        lk["hreflang"] = hreflang
        lk["href"] = abs_url(L, page)
        ref.insert_after(lk)
        ref = lk

    # link-based language switcher
    ls = soup.select_one(".lang-switch")
    if ls:
        ls.clear()
        for L in LANGS:
            a = soup.new_tag("a", href=path(L, page))
            a["data-lang"] = L
            if L == lang:
                a["class"] = ["active"]
            a.append(L.upper())
            ls.append(a)

    html = str(soup)
    # JSON-LD / og:image / twitter:image carry the literal origin -> swap for SITE
    html = html.replace("https://turar.art", SITE)
    return html + "\n"


def write_sitemap():
    def priority(page, lang):
        if page == "home":
            return "1.0" if lang == "en" else "0.8"
        return "0.8" if lang == "en" else "0.6"

    rows = []
    for page in PAGES:
        for lang in LANGS:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{L}" href="{abs_url(L, page)}"/>'
                for L in LANGS)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("en", page)}"/>'
            rows.append(
                f"  <url>\n    <loc>{abs_url(lang, page)}</loc>{alts}"
                f"\n    <changefreq>monthly</changefreq>"
                f"\n    <priority>{priority(page, lang)}</priority>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    with open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def main():
    with open(os.path.join(BASE, "i18n.json"), encoding="utf-8") as f:
        I18N = json.load(f)

    count = 0
    for page in PAGES:
        for lang in LANGS:
            out_rel = PAGES[page] if lang == "en" else os.path.join(lang, PAGES[page])
            out_abs = os.path.join(BASE, out_rel)
            os.makedirs(os.path.dirname(out_abs) or ".", exist_ok=True)
            with open(out_abs, "w", encoding="utf-8") as f:
                f.write(render(page, lang, I18N[lang]))
            count += 1
            print(f"  {out_rel}")
    write_sitemap()
    print(f"  sitemap.xml\nBuilt {count} pages for [{', '.join(LANGS)}] at SITE={SITE}")


if __name__ == "__main__":
    main()
