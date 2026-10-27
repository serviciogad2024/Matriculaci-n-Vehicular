#!/usr/bin/env python3
"""Generador estatico de matriculacionvehicular.com.

Uso:
    python build.py ESPECIFICACION.md [--out dist] [--strict]

Lee las paginas y las redirecciones del propio archivo de especificacion,
renderiza HTML con templates/base.html y valida enlaces, longitud y terminos
prohibidos. Con --strict, cualquier error detiene el build (codigo 1).
"""
import argparse
import datetime
import html as htmllib
import json
import pathlib
import re
import shutil
import sys

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = pathlib.Path(__file__).resolve().parent
DOMAIN = "https://matriculacionvehicular.com"
SITE_NAME = "Matriculación Vehicular Ecuador"
ADSENSE_CLIENT = "ca-pub-6946450094325847"
GA4_ID = "G-TP9QN2DS8J"
GSC_TOKEN = "fnYxgn5fFd7bc5J1QihxyOY9U16oa5MKU_UHpI1fbt8"
TODAY = datetime.date.today().isoformat()

# Palabras minimas (cuerpo, sin FAQ ni fuentes). Son una barrera, no el objetivo.
FLOORS = {"pilar": 550, "local": 280, "apoyo": 240, "hub": 150, "confianza": 24}
# Objetivo del plan SEO (se informa en build-report.md como brecha, no bloquea el build)
TARGETS = {"pilar": 1400, "local": 1100, "apoyo": 800, "hub": 600, "confianza": 350}
NO_ADS = {"contacto", "politica-de-privacidad", "politica-de-cookies", "aviso-legal",
          "sobre-nosotros", "metodologia-editorial", "fuentes-oficiales-ecuador", "404"}
NO_INDEX = {"politica-de-cookies", "aviso-legal", "404"}
FORBIDDEN = re.compile(r"\b(DGT|ITV|DNI|NIE|coches?|tenencia)\b")

NAV = [
    ("Calendario", "calendario-matriculacion-vehicular"),
    ("Valor y pago", "valor-a-pagar-matricula"),
    ("Revisión técnica", "revision-tecnica-vehicular"),
    ("Trámites", "tramites-vehiculares"),
    ("Ciudades", "matriculacion-por-ciudad"),
]
FOOTER = [
    ("Portales oficiales", "fuentes-oficiales-ecuador"),
    ("Metodología", "metodologia-editorial"),
    ("Sobre este sitio", "sobre-nosotros"),
    ("Contacto", "contacto"),
    ("Privacidad", "politica-de-privacidad"),
    ("Cookies", "politica-de-cookies"),
    ("Aviso legal", "aviso-legal"),
]

# Las marcas se construyen por partes para que este codigo, al estar incrustado en el .md, no se autodetecte.
_O, _C = "<!-" + "- ", " -" + "->"
PAGE_RE = re.compile(
    _O + "PAGE:" + r"START slug=(\S+)" + _C + r"\s*\n---\n(.*?)\n---\n(.*?)" + _O + "PAGE:" + "END" + _C, re.S)
RED_RE = re.compile(_O + "REDIRECTS:" + "START" + _C + "(.*?)" + _O + "REDIRECTS:" + "END" + _C, re.S)

DIGITS = [("1", "febrero"), ("2", "marzo"), ("3", "abril"), ("4", "mayo"), ("5", "junio"),
          ("6", "julio"), ("7", "agosto"), ("8", "septiembre"), ("9", "octubre"), ("0", "noviembre")]

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def url_of(slug):
    return "/" if slug == "index" else f"/{slug}/"


def plain(text):
    """Texto plano desde markdown/HTML simple (para JSON-LD y conteo)."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[*_`]", "", text).strip()


def md_inline(text):
    out = markdown.markdown(text, extensions=["sane_lists"])
    return re.sub(r"^<p>(.*)</p>$", r"\1", out.strip(), flags=re.S)


def render_md(body):
    md = markdown.Markdown(extensions=["tables", "sane_lists", "attr_list", "toc"])
    out = md.convert(body)
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out


def tool_html(name):
    if name == "digito":
        opts = "".join(f'<option value="{d}">{d}</option>' for d, _ in DIGITS)
        return ('<div class="tool" id="tool-digito"><label for="dig"><strong>¿Qué mes me toca?</strong> '
                'Elige el último dígito de tu placa</label>'
                f'<select id="dig"><option value="">Elige…</option>{opts}</select>'
                '<p id="res" aria-live="polite"></p></div>')
    if name == "arbol":
        items = [
            ("Quiero matricular mi vehículo este año", "matriculacion-anual-vehicular"),
            ("Compré un vehículo nuevo", "matriculacion-de-vehiculos-nuevos"),
            ("Traje un vehículo del exterior", "matriculacion-de-vehiculos-importados"),
            ("Compré o vendí un vehículo usado", "cambio-de-propietario-vehicular"),
            ("Perdí la matrícula", "duplicado-de-matricula-vehicular"),
            ("Perdí o me robaron las placas", "duplicado-de-placas-vehiculares"),
            ("Quiero cambiar el color, motor o carrocería", "cambio-de-caracteristicas-del-vehiculo"),
            ("Cambia el uso: particular a comercial", "cambio-de-servicio-vehicular"),
            ("Mi vehículo está bloqueado o con multas", "bloqueo-vehicular-desbloqueo"),
            ("Ya no usaré el vehículo", "baja-vehiculo"),
        ]
        lis = "".join(f'<li><a href="{url_of(s)}">{t}</a></li>' for t, s in items)
        return f'<ul class="arbol">{lis}</ul>'
    err(f"Herramienta desconocida: {name}")
    return ""


def load_spec(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    pages = {}
    for slug, fm, body in PAGE_RE.findall(text):
        meta = yaml.safe_load(fm) or {}
        meta["slug"] = slug
        meta["body"] = body.strip()
        if slug in pages:
            err(f"Slug duplicado en la especificación: {slug}")
        pages[slug] = meta
    redirects = []
    m = RED_RE.search(text)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line.startswith("/"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                redirects.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return pages, redirects


def breadcrumbs(pages, slug):
    trail, cur, seen = [], slug, set()
    while cur and cur not in seen:
        seen.add(cur)
        p = pages.get(cur)
        if not p:
            break
        trail.append((p.get("short") or p["h1"], url_of(cur)))
        cur = p.get("parent", "index") if cur != "index" else None
    return list(reversed(trail))


def build_jsonld(pages, p, crumbs, faq):
    slug = p["slug"]
    canonical = DOMAIN + url_of(slug)
    graph = [
        {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
         "name": SITE_NAME, "inLanguage": "es-EC"},
        {"@type": "Organization", "@id": DOMAIN + "/#org", "name": SITE_NAME, "url": DOMAIN + "/"},
    ]
    kind = p.get("schema", "Article")
    node = {"@type": kind, "@id": canonical + "#page", "url": canonical,
            "name": p["h1"], "headline": p["h1"], "description": p["description"],
            "inLanguage": "es-EC", "isPartOf": {"@id": DOMAIN + "/#website"}}
    if kind == "Article":
        node.update({"dateModified": str(p.get("updated", TODAY)),
                     "datePublished": str(p.get("published", p.get("updated", TODAY))),
                     "author": {"@id": DOMAIN + "/#org"}, "publisher": {"@id": DOMAIN + "/#org"},
                     "mainEntityOfPage": canonical})
    graph.append(node)
    if len(crumbs) > 1:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": DOMAIN + u}
            for i, (name, u) in enumerate(crumbs)]})
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(f["q"]),
             "acceptedAnswer": {"@type": "Answer", "text": plain(f["a"])}} for f in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    pages, redirects = load_spec(args.spec)
    for need in ("index", "404", "calendario-matriculacion-vehicular"):
        if need not in pages:
            err(f"Falta la página obligatoria: {need}")

    out = ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if (ROOT / "assets").exists():
        shutil.copytree(ROOT / "assets", out / "assets")
    has_fonts = (out / "assets" / "fonts" / "poppins-400.woff2").exists()
    if not has_fonts:
        warn("Faltan las fuentes Poppins en assets/fonts (se usará la fuente del sistema).")

    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")),
                      autoescape=select_autoescape(["html"]))
    tpl = env.get_template("base.html")
    linked_from = {s: set() for s in pages}
    verify_rows = []
    sitemap = []

    for slug, p in pages.items():
        for k in ("title", "description", "h1", "type"):
            if not p.get(k):
                err(f"[{slug}] falta el campo '{k}'")
        if len(str(p.get("title", ""))) > 60:
            warn(f"[{slug}] title de {len(p['title'])} caracteres (máx. 60)")
        if len(str(p.get("description", ""))) > 160:
            warn(f"[{slug}] description de {len(p['description'])} caracteres (máx. 160)")

        body = p["body"]
        body = re.sub(r"^\{\{TOOL:(\w+)\}\}$", lambda m: "\x00" + m.group(1) + "\x00", body, flags=re.M)
        body_html = render_md(body)
        body_html = re.sub(r"<p>\x00(\w+)\x00</p>", lambda m: tool_html(m.group(1)), body_html)

        words = len(plain(body_html).split())
        floor = FLOORS.get(p.get("type", "apoyo"), 0)
        if words < floor:
            (err if args.strict else warn)(f"[{slug}] {words} palabras < mínimo {floor} ({p.get('type')})")
        p["_words"] = words

        scan = plain(body_html) + " " + " ".join(f["q"] + " " + f["a"] for f in p.get("faq", []))
        for m in FORBIDDEN.finditer(scan):
            err(f"[{slug}] término prohibido: {m.group(0)}")

        for href in re.findall(r'href="(/[^"#?]*)', body_html):
            target = href.strip("/") or "index"
            if "." in target.split("/")[-1]:
                continue
            if target not in pages:
                err(f"[{slug}] enlace roto: {href}")
            elif target != slug:
                linked_from[target].add(slug)
        for r in p.get("related", []):
            if r not in pages:
                err(f"[{slug}] related inexistente: {r}")
            else:
                linked_from[r].add(slug)
        if p.get("parent", "index") not in pages and slug != "index":
            err(f"[{slug}] parent inexistente: {p.get('parent')}")

        faq = [{"q": f["q"], "a": f["a"], "a_html": md_inline(f["a"])} for f in p.get("faq", [])]
        sources = p.get("sources", [])
        related = [{"url": url_of(r), "title": pages[r].get("short") or pages[r]["h1"]}
                   for r in p.get("related", []) if r in pages]
        crumbs = breadcrumbs(pages, slug)
        robots = "noindex,follow" if slug in NO_INDEX else \
            "index,follow,max-image-preview:large,max-snippet:-1"
        ads = slug not in NO_ADS
        ctx = dict(
            page=p, body=body_html, faq=faq, sources=sources, related=related, crumbs=crumbs,
            canonical=DOMAIN + url_of(slug), robots=robots, ads=ads, client=ADSENSE_CLIENT,
            ga4=GA4_ID, gsc=GSC_TOKEN, site_name=SITE_NAME, has_fonts=has_fonts,
            nav=[(t, url_of(s)) for t, s in NAV], footer=[(t, url_of(s)) for t, s in FOOTER],
            updated=str(p.get("updated", TODAY)), is_home=(slug == "index"),
            jsonld=build_jsonld(pages, p, crumbs, faq), og_image=DOMAIN + "/assets/og-default.jpg",
            slug=slug)
        page_html = tpl.render(**ctx)

        if slug == "404":
            (out / "404.html").write_text(page_html, encoding="utf-8")
        else:
            d = out if slug == "index" else out / slug
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(page_html, encoding="utf-8")
        if slug not in NO_INDEX:
            sitemap.append((DOMAIN + url_of(slug), ctx["updated"]))
        for v in p.get("verify", []):
            verify_rows.append((slug, v))

    for slug, srcs in linked_from.items():
        if slug in ("index", "404"):
            continue
        if not srcs and slug not in {s for _, s in NAV} | {s for _, s in FOOTER}:
            warn(f"Página huérfana (nadie la enlaza desde el contenido): {slug}")

    page_urls = {url_of(s) for s in pages}
    for src, code, dest in redirects:
        if src in page_urls:
            err(f"La redirección {src} choca con una página viva")
        if code == "301" and dest not in page_urls:
            err(f"Destino de redirección inexistente: {src} -> {dest}")

    # --- archivos de raiz ---
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in sitemap)
        + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\n"
        "User-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\n"
        f"Sitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    (out / "ads.txt").write_text(
        "google.com, pub-6946450094325847, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    llms = [f"# {SITE_NAME}", "",
            "> Guía informativa independiente sobre matriculación y trámites vehiculares en Ecuador. "
            "No es un sitio oficial.", "", "## Páginas", ""]
    for s, p in pages.items():
        if s not in NO_INDEX:
            llms.append(f"- [{p['h1']}]({DOMAIN}{url_of(s)}): {p['description']}")
    (out / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    (out / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n", encoding="utf-8")

    red301 = [(s, d) for s, c, d in redirects if c == "301"]
    gone = [s for s, c, d in redirects if c == "410"]
    (out / "_redirects").write_text(
        "# 301 generado por build.py. Las URL eliminadas (410) no se listan: devuelven 404 en este hosting.\n"
        + "".join(f"{s}  {d}  301\n" for s, d in red301)
        + "/category/*  /tramites-vehiculares/  301\n", encoding="utf-8")
    (out / ".htaccess").write_text(
        "DirectoryIndex index.html\nErrorDocument 404 /404.html\nRewriteEngine On\n"
        "RewriteCond %{HTTPS} !=on [OR]\nRewriteCond %{HTTP_HOST} ^www\\. [NC]\n"
        f"RewriteRule ^ {DOMAIN}%{{REQUEST_URI}} [L,R=301]\n\n"
        + "".join(f"Redirect 301 {s} {DOMAIN}{d}\n" for s, d in red301)
        + "".join(f"Redirect gone {s}\n" for s in gone)
        + f"RedirectMatch 301 ^/category/.*$ {DOMAIN}/tramites-vehiculares/\n", encoding="utf-8")

    report = ["# Informe de build", "", f"Páginas: {len(pages)} · Redirecciones 301: {len(red301)} · 410: {len(gone)}", "",
              "## Errores", *(f"- {e}" for e in errors or ["ninguno"]), "",
              "## Avisos", *(f"- {w}" for w in warnings or ["ninguno"]), "",
              "## Datos a verificar antes de publicar", *(f"- [{s}] {v}" for s, v in verify_rows or [("-", "ninguno")]), "",
              "## Palabras por página (actual / objetivo del plan)",
              *(f"- {s}: {p['_words']} / {TARGETS.get(p['type'], 0)} ({p['type']})"
                + ("  → ampliar con datos verificados" if p['_words'] < TARGETS.get(p['type'], 0) * 0.8 and s != "404" else "")
                for s, p in pages.items())]
    (ROOT / "build-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"{len(pages)} páginas · {len(errors)} errores · {len(warnings)} avisos · informe: build-report.md")
    if errors and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
