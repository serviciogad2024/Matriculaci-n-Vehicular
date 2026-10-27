# Matriculación Vehicular Ecuador: guía completa para generar el sitio estático en HTML

> Documento maestro de migración de **matriculacionvehicular.com** (WordPress) a sitio estático.
> Versión del 2026-10-27. Contiene **(1)** todas las instrucciones y el código para generar el sitio completo y **(2)** el contenido publicable de las **46 URL** (25 que se mantienen y mejoran, 21 nuevas) más la página 404, el mapa de redirecciones 301/410 de los 180 posts antiguos y la tabla de datos que hay que verificar antes de publicar.

## 0. Lee esto primero

**Qué es este archivo.** Es a la vez la guía y la fuente del sitio: el generador (`build.py`) lee este mismo `.md`, toma cada bloque `PAGE:START … PAGE:END` y produce el HTML. Editas el contenido aquí, ejecutas el build y obtienes la carpeta `dist/` lista para publicar.

**Estado honesto del contenido.**

1. **Los montos son de referencia.** Donde un valor cambia cada año (impuesto por avalúo, SPPAT, tasas, multas sobre el SBU, tarifas de revisión técnica por ciudad) el texto lo presenta como referencia o remite al portal oficial. La sección 10 lista cada dato que debes confirmar antes de publicar. No publiques una cifra sin contrastarla.
2. **Longitud.** Las páginas cumplen mínimos de calidad (pilares ≥ 550 palabras de cuerpo, locales ≥ 280, apoyo ≥ 240) pero **quedan por debajo de los objetivos del plan SEO** (pilar 1.400, local 1.100, apoyo 800, hub 600). El informe `build-report.md` muestra la brecha por página. La ampliación correcta es con datos oficiales verificados (tablas de tarifas, calendarios por ciudad, capturas de procesos), no con relleno: ese es el siguiente trabajo, empezando por Quito, Guayaquil, Cuenca, Riobamba y Ambato.
3. **Ambato y Riobamba** no tienen aún datos locales verificados (entidad gestora, centro de revisión, tarifas). Se publican con el marco nacional y la forma de confirmar cada dato. Riobamba fue la única página con clics en 2026: verifícala primero.
4. **Identificadores incluidos en el código** (`ca-pub-6946450094325847`, GA4 `G-TP9QN2DS8J`, token de Search Console): verifica que sean los vigentes en el sitio actual. El correo `contacto@matriculacionvehicular.com` es un marcador: crea esa cuenta o cámbialo.
5. **Imágenes.** Hay que copiar del WordPress actual el logo y los iconos (sección 3.4). Sin ellos el sitio se ve, pero con la imagen del logo rota.

## 1. Contexto y decisiones de diseño

### 1.1 Por qué se rehace

- Las impresiones en Search Console cayeron de **13.403 (jul 2025)** a **68 (oct 2026)** y la posición media pasó de 14–20 a 54–65.
- El **42 %** de las impresiones venía de España, con contenido contaminado (DGT, ITV, «coche»).
- **Bing** aporta cerca del 68 % de las sesiones: conviene Bing Webmaster Tools e IndexNow desde el primer día.
- Las páginas que funcionaban eran específicas: cambio de color/motor/carrocería, servicio particular vs. comercial, requisitos de placas, costos de traspaso, baja y Riobamba.
- Competidores: matriculacionvehicular.ec (DR 12) y ecuadorlegalonline.com (DR 43).

### 1.2 Principios

1. **Responder la intención en las primeras líneas** (bloque «Respuesta rápida»).
2. **Un tema, una URL.** Los 180 posts antiguos se fusionan en las páginas pilares con 301 o se eliminan con 410.
3. **Cero contenido de España.** El build falla si aparecen `DGT`, `ITV`, `DNI`, `NIE`, `coche(s)` o `tenencia`.
4. **Sitio no oficial, con fecha visible y fuentes** en cada página.
5. **Monetización sin bloques manuales:** solo el script de AdSense (Auto ads) en el `<head>`; no hay `<ins class="adsbygoogle">` en ninguna plantilla.

### 1.3 Paleta y tipografía (tomadas del diseño actual)

| Token | Valor | Uso |
|---|---|---|
| `--blue` | `#1D4F91` | Botón primario (texto blanco), enlaces, pie de página, cabeceras de tabla |
| `--blue-dark` | `#14396B` | Hover del botón y de enlaces |
| `--sky` | `#B3C8D9` | Fondo del hero, bordes de herramientas y tarjetas |
| `--yellow` | `#FFD100` | Cabecera del sitio y `theme-color` |
| `--amber` | `#F7B718` | Botón secundario (texto `#1D4F91`), acentos, borde inferior de cabecera |
| `--ink` | `#181818` | Texto |
| `--bg` | `#FFFFFF` | Fondo |
| `--line` | `#D1D5DB` | Bordes de campos y tablas (radio 2 px en campos, 8 px en botones) |
| `--soft` / `--cream` | `#EEF3F8` / `#FFF8DC` | Tintes derivados de celeste y amarillo para cajas |

Tipografía: **Poppins** 400 y 600 (autoalojada, `font-display: swap`).

Contraste: texto `#181818` sobre amarillo y celeste y blanco sobre `#1D4F91` superan 4,5:1. El enlace en el cuerpo es `#1D4F91` subrayado.

## 2. Estructura del repositorio

```
matriculacion-vehicular/
├── matriculacion-vehicular-sitio-completo.md   <- este archivo (fuente de contenido)
├── build.py                                    <- generador
├── requirements.txt
├── templates/base.html
├── assets/
│   ├── style.css
│   ├── app.js
│   ├── fonts/poppins-400.woff2, poppins-600.woff2
│   ├── logo.png, logo-270.png, favicon-32.png, og-default.jpg
└── dist/                                        <- salida (no se versiona)
```

> **El repositorio de GitHub debe ser privado.** Créalo como privado y no lo cambies a público: `gh repo create matriculacion-vehicular --private`.

## 3. Puesta en marcha

### 3.1 Extraer los archivos de este .md

Guarda el siguiente script como `bootstrap.py` junto a este `.md` y ejecútalo: crea `build.py`, `templates/base.html`, `assets/style.css`, `assets/app.js`, `requirements.txt` y `.gitignore` a partir de los bloques de código de la sección 4.

```python
import pathlib, re, sys
md = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
pat = re.compile(r"```[a-z]*\n(?:#|<!--|/\*) FILE: (\S+)[^\n]*\n(.*?)\n```", re.S)
for name, body in pat.findall(md):
    p = pathlib.Path(name); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body.rstrip() + "\n", encoding="utf-8"); print("escrito", name)
```

```bash
python3 bootstrap.py matriculacion-vehicular-sitio-completo.md
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py matriculacion-vehicular-sitio-completo.md --out dist --strict
python -m http.server 8080 -d dist      # abre http://localhost:8080
```

`--strict` detiene el build si hay enlaces rotos, términos prohibidos, páginas por debajo del mínimo, destinos de redirección inexistentes o redirecciones que chocan con una página viva. Sin `--strict` esos casos se informan pero el build continúa. Siempre se escribe `build-report.md` con errores, avisos, datos a verificar y palabras por página.

### 3.2 Fuentes Poppins

```bash
mkdir -p assets/fonts && cd assets/fonts
curl -LO https://cdn.jsdelivr.net/fontsource/fonts/poppins@latest/latin-400-normal.woff2 && mv latin-400-normal.woff2 poppins-400.woff2
curl -LO https://cdn.jsdelivr.net/fontsource/fonts/poppins@latest/latin-600-normal.woff2 && mv latin-600-normal.woff2 poppins-600.woff2
```

Si el build avisa «Faltan las fuentes Poppins», no se encontraron y el sitio usa la fuente del sistema (funciona, pero cambia el aspecto).

### 3.3 Logo e iconos

Descarga del WordPress actual (Medios) el logo y guárdalos como: `assets/logo.png` (alto aproximado 48 px, se muestra a 160×48), `assets/logo-270.png` (icono táctil), `assets/favicon-32.png` (32×32) y `assets/og-default.jpg` (1200×630, para redes sociales; puedes componerlo con el logo sobre fondo `#FFD100`).

### 3.4 Comportamiento del generador

- Cada página se declara con un bloque entre las marcas `PAGE:START slug=… ` y `PAGE:END`, con un front matter YAML y cuerpo en Markdown.
- Las herramientas se insertan con `{{TOOL:digito}}` (selector de dígito de placa) y `{{TOOL:arbol}}` (árbol «¿qué trámite necesitas?»).
- Genera: `index.html` por carpeta, `404.html`, `sitemap.xml` (con `lastmod` real = campo `updated`), `robots.txt`, `ads.txt`, `llms.txt`, `_headers`, `_redirects` y `.htaccess`.
- JSON-LD automático: `WebSite`, `Organization`, el tipo de la página (`Article`, `HowTo`, `CollectionPage`, `WebPage`), `BreadcrumbList` y `FAQPage` cuando hay preguntas.
- Las migas de pan se construyen con el campo `parent` (por defecto, la portada).
- Las páginas legales de cookies y aviso legal y la 404 llevan `noindex` y no entran al sitemap.

### 3.5 Formato de una página (front matter)

```yaml
title: "Máx. 60 caracteres"            # <title>
description: "Máx. 160 caracteres"     # meta description
h1: "Título visible"
short: "Nombre corto para migas y tarjetas"
type: pilar | local | apoyo | hub | confianza
parent: slug-del-padre                 # opcional (por defecto: portada)
schema: Article | HowTo | CollectionPage | WebPage
updated: 2026-10-27                    # fecha visible y lastmod del sitemap
quick: "Respuesta rápida en 1-2 frases"
related: [slug1, slug2]                # tarjetas «Sigue leyendo» (y cuenta como enlace interno)
sources: [{t: "Nombre", u: "https://..."}]
faq: [{q: "Pregunta", a: "Respuesta (admite Markdown)"}]
verify: ["Dato que debe confirmarse antes de publicar"]
```

## 4. Código completo

Los bloques con la primera línea `FILE:` son los que extrae `bootstrap.py`.

### `requirements.txt` y `.gitignore`

```text
# FILE: requirements.txt
markdown>=3.5
pyyaml>=6.0
jinja2>=3.1
```

```text
# FILE: .gitignore
dist/
.venv/
__pycache__/
```

### `build.py`

```python
# FILE: build.py
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
```

### `templates/base.html`

```html
<!-- FILE: templates/base.html -->
<!doctype html>
<html lang="es-EC">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ page.title }}</title>
<meta name="description" content="{{ page.description }}">
<link rel="canonical" href="{{ canonical }}">
<meta name="robots" content="{{ robots }}">
<meta name="theme-color" content="#FFD100">
<meta name="google-site-verification" content="{{ gsc }}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/logo-270.png">
<meta property="og:locale" content="es_EC">
<meta property="og:type" content="{{ 'website' if is_home else 'article' }}">
<meta property="og:site_name" content="{{ site_name }}">
<meta property="og:title" content="{{ page.title }}">
<meta property="og:description" content="{{ page.description }}">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:image" content="{{ og_image }}">
<meta name="twitter:card" content="summary_large_image">
{% if has_fonts %}<link rel="preload" href="/assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>{% endif %}
<link rel="stylesheet" href="/assets/style.css">
{% if ads %}<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{ client }}" crossorigin="anonymous"></script>{% endif %}
<script async src="https://www.googletagmanager.com/gtag/js?id={{ ga4 }}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','{{ ga4 }}');</script>
<script type="application/ld+json">{{ jsonld|safe }}</script>
</head>
<body class="{{ 'home' if is_home else 'inner' }}">
<a class="skip" href="#main">Saltar al contenido</a>
<div class="aviso-top">Sitio informativo independiente, <strong>no oficial</strong>. Los trámites y pagos se hacen en los portales oficiales.</div>
<header class="site-header">
  <div class="wrap header-in">
    <a class="brand" href="/" aria-label="{{ site_name }}: inicio">
      <img src="/assets/logo.png" alt="Matriculación Vehicular" width="160" height="48">
    </a>
    <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Abrir menú">
    <label for="menu-toggle" class="menu-btn" aria-hidden="true">Menú</label>
    <nav class="main-nav" aria-label="Principal">
      <ul>{% for t, u in nav %}<li><a href="{{ u }}"{% if u == '/' ~ slug ~ '/' %} aria-current="page"{% endif %}>{{ t }}</a></li>{% endfor %}</ul>
    </nav>
  </div>
</header>

{% if is_home %}
<section class="hero">
  <div class="wrap">
    <h1>{{ page.h1 }}</h1>
    {% if page.lead %}<p class="lead">{{ page.lead }}</p>{% endif %}
    {% if page.ctas %}<p class="cta-row">{% for c in page.ctas %}<a class="btn {{ 'btn-secondary' if c.style == 'secondary' else '' }}" href="{{ c.u }}">{{ c.t }}</a>{% endfor %}</p>{% endif %}
  </div>
</section>
{% endif %}

<main id="main" class="wrap content">
  {% if not is_home %}
  {% if crumbs|length > 1 %}
  <nav class="crumbs" aria-label="Migas de pan"><ol>
    {% for name, u in crumbs %}<li>{% if not loop.last %}<a href="{{ u }}">{{ name }}</a>{% else %}<span aria-current="page">{{ name }}</span>{% endif %}</li>{% endfor %}
  </ol></nav>
  {% endif %}
  <h1>{{ page.h1 }}</h1>
  {% if page.type not in ['confianza'] or page.show_date %}<p class="meta">Actualizado: <time datetime="{{ updated }}">{{ updated }}</time> · Sitio informativo no oficial</p>{% endif %}
  {% endif %}

  {% if page.quick %}<div class="respuesta"><strong>Respuesta rápida:</strong> {{ page.quick }}</div>{% endif %}

  <article class="prose">
  {{ body|safe }}
  </article>

  {% if faq %}
  <section class="faq" aria-labelledby="faq-h"><h2 id="faq-h">Preguntas frecuentes</h2>
    {% for f in faq %}<details><summary>{{ f.q }}</summary><div>{{ f.a_html|safe }}</div></details>{% endfor %}
  </section>
  {% endif %}

  {% if sources %}
  <section class="fuentes"><h2>Fuentes oficiales y de referencia</h2>
    <ul>{% for s in sources %}<li><a href="{{ s.u }}" rel="noopener" target="_blank">{{ s.t }}</a></li>{% endfor %}</ul>
    <p class="small">Los datos de dinero, plazos y normas pueden cambiar. Confírmalos siempre en el portal oficial antes de pagar o tramitar.</p>
  </section>
  {% endif %}

  {% if related %}
  <section class="related"><h2>Sigue leyendo</h2>
    <ul class="cards">{% for r in related %}<li><a href="{{ r.url }}">{{ r.title }}</a></li>{% endfor %}</ul>
  </section>
  {% endif %}
</main>

<footer class="site-footer">
  <div class="wrap">
    <p><strong>{{ site_name }}</strong> es una guía informativa independiente. No pertenece al Gobierno de Ecuador, a la ANT, al SRI ni a ningún municipio.</p>
    <ul class="footer-links">{% for t, u in footer %}<li><a href="{{ u }}">{{ t }}</a></li>{% endfor %}</ul>
    <p class="small">© 2026 matriculacionvehicular.com · Información revisada cada mes con fuentes oficiales.</p>
  </div>
</footer>
<script src="/assets/app.js" defer></script>
</body>
</html>
```

### `assets/style.css`

```css
/* FILE: assets/style.css */
/* Tokens tomados del diseño actual (tema WordPress): azul #1D4F91, celeste #B3C8D9,
   amarillo #FFD100, ámbar #F7B718, texto #181818, Poppins, botones con radio 8px.
   Derivados: --soft (#EEF3F8) y --cream (#FFF8DC) son tintes de celeste y amarillo. */
@font-face{font-family:"Poppins";font-weight:400;font-style:normal;font-display:swap;src:url("/assets/fonts/poppins-400.woff2") format("woff2")}
@font-face{font-family:"Poppins";font-weight:600;font-style:normal;font-display:swap;src:url("/assets/fonts/poppins-600.woff2") format("woff2")}
:root{
  --blue:#1D4F91; --blue-dark:#14396B; --sky:#B3C8D9; --yellow:#FFD100; --amber:#F7B718;
  --ink:#181818; --bg:#FFFFFF; --line:#D1D5DB; --soft:#EEF3F8; --cream:#FFF8DC;
  --radius:8px; --measure:46rem;
  --font:"Poppins",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--font);font-size:1.0625rem;line-height:1.7;color:var(--ink);background:var(--bg)}
img{max-width:100%;height:auto}
a{color:var(--blue);text-decoration:underline;text-underline-offset:2px}
a:hover{color:var(--blue-dark)}
:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.wrap{width:100%;max-width:70rem;margin:0 auto;padding:0 1rem}
.skip{position:absolute;left:-999px;top:0;background:var(--blue);color:#fff;padding:.5rem 1rem;z-index:50}
.skip:focus{left:0}

.aviso-top{background:var(--ink);color:#fff;font-size:.8125rem;text-align:center;padding:.4rem 1rem;line-height:1.4}
.site-header{background:var(--yellow);border-bottom:4px solid var(--amber);position:relative}
.header-in{display:flex;align-items:center;justify-content:space-between;min-height:4.25rem;gap:1rem}
.brand img{display:block;height:auto;width:10rem}
.main-nav ul{list-style:none;margin:0;padding:0;display:flex;gap:.25rem}
.main-nav a{display:block;padding:.6rem .9rem;color:var(--ink);text-decoration:none;font-weight:600;border-radius:var(--radius)}
.main-nav a:hover,.main-nav a[aria-current]{background:rgba(255,255,255,.55)}
.menu-toggle{position:absolute;opacity:0;pointer-events:none}
.menu-btn{display:none;cursor:pointer;font-weight:600;padding:.5rem .9rem;border:2px solid var(--ink);border-radius:var(--radius)}
@media(max-width:52rem){
  .menu-btn{display:inline-block}
  .main-nav{display:none;position:absolute;left:0;right:0;top:100%;background:var(--yellow);border-bottom:4px solid var(--amber);z-index:20}
  .menu-toggle:checked ~ .main-nav{display:block}
  .menu-toggle:focus-visible + .menu-btn{outline:3px solid var(--blue);outline-offset:2px}
  .main-nav ul{flex-direction:column;padding:.5rem 1rem 1rem}
}

.hero{background:var(--sky);padding:2.5rem 0 2.25rem}
.hero h1{font-size:clamp(1.9rem,5vw,3rem);line-height:1.15;margin:0 0 .75rem;max-width:22ch}
.hero .lead{font-size:1.15rem;max-width:44rem;margin:0 0 1.25rem}
.cta-row{display:flex;flex-wrap:wrap;gap:.75rem;margin:0}
.btn{display:inline-block;background:var(--blue);color:#fff;border:2px solid var(--blue);border-radius:var(--radius);padding:.7rem 1.25rem;font-weight:600;text-decoration:none;min-height:2.75rem}
.btn:hover{background:var(--blue-dark);border-color:var(--blue-dark);color:#fff}
.btn-secondary{background:var(--amber);border-color:var(--amber);color:var(--blue-dark)}
.btn-secondary:hover{background:var(--yellow);border-color:var(--yellow);color:var(--blue-dark)}

.content{padding-top:1.5rem;padding-bottom:3rem}
.content>h1,.content>.meta,.content>.respuesta,.content>.prose,.content>.faq,.content>.fuentes,.content>.related,.content>.crumbs{max-width:var(--measure)}
.content>h1{font-size:clamp(1.75rem,4.5vw,2.5rem);line-height:1.2;margin:.25rem 0 .5rem}
.meta{color:#4B5563;font-size:.875rem;margin:0 0 1.25rem}
.crumbs ol{list-style:none;display:flex;flex-wrap:wrap;gap:.25rem;padding:0;margin:0 0 .5rem;font-size:.875rem}
.crumbs li+li::before{content:"›";margin-right:.25rem;color:#6B7280}
.crumbs a{color:var(--blue)}
.respuesta{background:var(--cream);border-left:6px solid var(--amber);padding:1rem 1.25rem;margin:0 0 1.5rem;border-radius:0 var(--radius) var(--radius) 0}
.prose h2{font-size:1.5rem;line-height:1.3;margin:2.25rem 0 .75rem}
.prose h3{font-size:1.2rem;margin:1.75rem 0 .5rem}
.prose p,.prose ul,.prose ol{margin:0 0 1.1rem}
.prose li{margin:.3rem 0}
.prose blockquote{margin:1.25rem 0;padding:.75rem 1.25rem;background:var(--soft);border-left:6px solid var(--sky);border-radius:0 var(--radius) var(--radius) 0}
.table-wrap{overflow-x:auto;margin:0 0 1.4rem}
table{border-collapse:collapse;width:100%;font-size:.95rem}
th{background:var(--blue);color:#fff;text-align:left}
th,td{padding:.6rem .75rem;border:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(even){background:var(--soft)}

.tool{background:var(--soft);border:2px solid var(--sky);border-radius:var(--radius);padding:1rem 1.25rem;margin:0 0 1.5rem}
.tool label{display:block;margin-bottom:.5rem}
.tool select{font:inherit;padding:.55rem .75rem;border:1px solid var(--line);border-radius:2px;background:#fff;min-width:9rem;box-shadow:inset 0 1px 3px #f6f6f7}
.tool p{margin:.75rem 0 0;font-weight:600}
ul.arbol{list-style:none;padding:0;display:grid;gap:.6rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
ul.arbol a{display:block;padding:.8rem 1rem;background:var(--soft);border:2px solid var(--sky);border-radius:var(--radius);text-decoration:none;font-weight:600}
ul.arbol a:hover{background:var(--yellow);border-color:var(--amber);color:var(--ink)}

.faq{margin:2.5rem 0 0}
.faq h2,.fuentes h2,.related h2{font-size:1.4rem}
details{border:1px solid var(--line);border-radius:var(--radius);margin:0 0 .6rem;background:#fff}
summary{cursor:pointer;padding:.8rem 1rem;font-weight:600;list-style:none}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";float:right;font-weight:600;color:var(--blue)}
details[open] summary::after{content:"–"}
details>div{padding:0 1rem .9rem}
.fuentes{margin:2.5rem 0 0;padding:1rem 1.25rem;background:var(--soft);border-radius:var(--radius)}
.fuentes ul{margin:.5rem 0}
.small{font-size:.85rem;color:#4B5563}
.related{margin:2.5rem 0 0}
.cards{list-style:none;padding:0;display:grid;gap:.75rem;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr))}
.cards a{display:block;padding:.9rem 1rem;border:2px solid var(--sky);border-radius:var(--radius);text-decoration:none;font-weight:600;height:100%}
.cards a:hover{border-color:var(--amber);background:var(--cream)}

.site-footer{background:var(--blue);color:#fff;padding:2rem 0;margin-top:2rem}
.site-footer a{color:#fff}
.site-footer .small{color:#DCE6F2}
.footer-links{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:.5rem 1.25rem;margin:1rem 0}
@media print{.site-header,.aviso-top,.site-footer,.menu-btn{display:none}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
```

### `assets/app.js`

```javascript
/* FILE: assets/app.js */
(function () {
  var sel = document.getElementById('dig');
  if (!sel) return;
  var months = {1:'febrero',2:'marzo',3:'abril',4:'mayo',5:'junio',6:'julio',7:'agosto',8:'septiembre',9:'octubre',0:'noviembre'};
  var idx = {1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:10};
  var out = document.getElementById('res');
  sel.addEventListener('change', function () {
    var v = sel.value;
    if (v === '') { out.textContent = ''; return; }
    var now = new Date().getMonth();
    var d = idx[v] - now;
    var msg = 'Tu mes de matriculación es ' + months[v] + '. ';
    if (d === 0) msg += 'Es este mes: aprovéchalo antes de que termine.';
    else if (d > 0) msg += 'Faltan ' + d + (d === 1 ? ' mes.' : ' meses.');
    else msg += 'Ya pasó este año: revisa recargos y multas pendientes.';
    out.textContent = msg + ' Diciembre es para rezagados, con recargos.';
  });
})();
```

## 5. Monetización, analítica y señales técnicas

### 5.1 AdSense sin bloques manuales

- La plantilla incluye **solo** el cargador `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6946450094325847" crossorigin="anonymous"></script>` en el `<head>`. No hay unidades de anuncio escritas a mano.
- **Las páginas legales, de contacto, «Sobre este sitio», «Metodología» y «Portales oficiales» no cargan el script** (conjunto `NO_ADS` en `build.py`).
- En la consola de AdSense, para el sitio: activa **Auto ads** con formatos dentro de la página; deja anclas, viñetas (vignette) y laterales **apagados** al inicio; carga publicitaria baja; revisa el CLS en Search Console tras una semana y sube la carga de forma gradual.
- `ads.txt` se genera con `google.com, pub-6946450094325847, DIRECT, f08c47fec0942fa0`.
- No se usan anuncios en el selector de dígito ni en el cuadro de respuesta rápida; Auto ads decide la ubicación en el cuerpo del texto.
- Mensaje de consentimiento (CMP): si recibes tráfico del EEE/Reino Unido, configura el mensaje de consentimiento en AdSense (Privacidad y mensajes). El tráfico objetivo es Ecuador.

### 5.2 Analítica y propiedad

- **GA4** en todas las páginas (`gtag.js`), con el ID definido en `build.py` (`GA4_ID`).
- **Search Console:** meta de verificación incluida (`GSC_TOKEN`). Mantén la propiedad y envía `https://matriculacionvehicular.com/sitemap.xml`.
- **Bing Webmaster Tools:** importa la propiedad desde Search Console (o verifica por DNS) y envía el mismo sitemap.

### 5.3 IndexNow (Bing)

Genera una clave aleatoria de 32 caracteres, guarda `dist/<clave>.txt` con la propia clave dentro (colócalo en `assets/` y cópialo a la raíz) y notifica tras cada despliegue:

```bash
curl -X POST "https://api.indexnow.org/indexnow" -H "Content-Type: application/json" \
  -d '{"host":"matriculacionvehicular.com","key":"TU_CLAVE","keyLocation":"https://matriculacionvehicular.com/TU_CLAVE.txt","urlList":["https://matriculacionvehicular.com/calendario-matriculacion-vehicular/"]}'
```

### 5.4 Reglas de URL y canonicalidad

- Dominio canónico: `https://matriculacionvehicular.com` (sin `www`), con barra final.
- `www` → raíz con 301; http → https en el hosting.
- Los slugs existentes **no cambian**. No hay años en las URL.
- `robots.txt` permite a todos los rastreadores, incluidos los de IA; `llms.txt` resume el sitio.

## 6. Publicación (hosting)

Cualquier hosting estático sirve. Con **Cloudflare Pages** o **Netlify**:

1. Sube el repositorio **privado** a GitHub y conéctalo al hosting (ambos soportan repositorios privados).
2. Comando de build: `pip install -r requirements.txt && python build.py matriculacion-vehicular-sitio-completo.md --out dist --strict`
3. Directorio de salida: `dist`. Variable de entorno: `PYTHON_VERSION=3.11`.
4. Dominio: apunta el DNS al hosting solo cuando la vista previa esté revisada; activa HTTPS y la redirección de `www` a la raíz.
5. `_redirects` (ya generado) contiene los **172 redirects 301**. Las **8 URL con 410** no se escriben en `_redirects` porque Cloudflare Pages no admite el estado 410: devuelven la 404 del sitio, algo que Google trata de forma equivalente a medio plazo. En Netlify puedes añadir una línea por URL con estado `410`. Con Apache, `.htaccess` ya incluye `Redirect gone`.
6. Mantén el WordPress en un subdominio privado o una copia de seguridad hasta confirmar que las redirecciones responden bien.

## 7. Contenido, estructura y mapa de URL

Reglas editoriales que aplican a cada página:

- Bloque **«Respuesta rápida»** al inicio; el resto solo desarrolla.
- Una sola frase de cada dato importante (mes, plazo, monto de referencia) y enlace a la guía que lo amplía.
- Aviso de **sitio no oficial** visible (barra superior y pie) y fecha de actualización.
- Fuentes al pie (`sources`) con el portal oficial; los datos inciertos van también en `verify`.
- Preguntas frecuentes reales y cortas (alimentan `FAQPage`).
- Enlaces internos: cada página enlaza a su padre y a 3–6 relacionadas; ninguna queda huérfana (el build avisa).

### 7.1 Mapa completo de URL

| # | URL | Estado | Tipo | Title |
|---|---|---|---|---|
| 1 | `/` | MANTENER | hub | Matriculación vehicular en Ecuador 2026: guía clara |
| 2 | `/calendario-matriculacion-vehicular/` | NUEVA | pilar | Calendario de matriculación vehicular Ecuador 2026 |
| 3 | `/valor-a-pagar-matricula/` | NUEVA | pilar | Valor a pagar de la matrícula vehicular en Ecuador |
| 4 | `/multas-por-no-matricular-vehiculo/` | NUEVA | pilar | Multas por no matricular el vehículo en Ecuador |
| 5 | `/matriculacion-anual-vehicular/` | MANTENER + MEJORAR | pilar | Matriculación anual vehicular en Ecuador: guía 2026 |
| 6 | `/revision-tecnica-vehicular/` | NUEVA | pilar | Revisión técnica vehicular en Ecuador: guía 2026 |
| 7 | `/cambio-de-propietario-vehicular/` | MANTENER + MEJORAR | pilar | Cambio de propietario de vehículo en Ecuador |
| 8 | `/cambio-de-caracteristicas-del-vehiculo/` | MANTENER + MEJORAR | pilar | Cambio de color, motor o carrocería de un vehículo |
| 9 | `/matriculacion-de-vehiculos-nuevos/` | MANTENER + MEJORAR | pilar | Matriculación de vehículos nuevos en Ecuador |
| 10 | `/matriculacion-vehicular-quito/` | MANTENER + MEJORAR | local | Matriculación vehicular en Quito: pasos y requisitos |
| 11 | `/matriculacion-vehicular-guayaquil/` | MANTENER + MEJORAR | local | Matriculación vehicular en Guayaquil: guía práctica |
| 12 | `/matriculacion-vehicular-cuenca/` | MANTENER + MEJORAR | local | Matriculación vehicular en Cuenca: guía práctica |
| 13 | `/matriculacion-vehicular-ambato/` | MANTENER + MEJORAR | local | Matriculación vehicular en Ambato: cómo hacerlo |
| 14 | `/matriculacion-vehicular-riobamba/` | MANTENER + MEJORAR | local | Matriculación vehicular en Riobamba: guía práctica |
| 15 | `/revision-tecnica-vehicular-quito/` | NUEVA | local | Revisión técnica vehicular en Quito: costos 2026 |
| 16 | `/revision-tecnica-vehicular-guayaquil/` | NUEVA | local | Revisión técnica vehicular en Guayaquil: costos 2026 |
| 17 | `/revision-tecnica-vehicular-cuenca/` | NUEVA | local | Revisión técnica vehicular en Cuenca: centros y pasos |
| 18 | `/certificado-unico-vehicular/` | NUEVA | apoyo | Certificado Único Vehicular (CUV): qué es y cómo pedirlo |
| 19 | `/matricula-moto/` | NUEVA | apoyo | Matrícula de moto en Ecuador: pasos, requisitos y costos |
| 20 | `/sppat/` | NUEVA | apoyo | SPPAT: qué es, cuánto cuesta y cómo consultarlo |
| 21 | `/vehiculos-electricos-exoneracion-matricula/` | NUEVA | apoyo | Vehículos eléctricos: exoneración en la matrícula |
| 22 | `/rebaja-matricula-adultos-mayores-discapacidad/` | NUEVA | apoyo | Rebaja de matrícula para adultos mayores y discapacidad |
| 23 | `/bloqueo-vehicular-desbloqueo/` | NUEVA | apoyo | Bloqueo vehicular: causas y cómo desbloquear |
| 24 | `/turno-matriculacion-vehicular/` | NUEVA | apoyo | Turno de matriculación vehicular: cómo agendarlo |
| 25 | `/duplicado-de-placas-vehiculares/` | NUEVA | apoyo | Duplicado de placas vehiculares: pasos y costos |
| 26 | `/matriculacion-de-vehiculos-importados/` | MANTENER + MEJORAR | apoyo | Matriculación de vehículos importados en Ecuador |
| 27 | `/permiso-de-circulacion-temporal/` | MANTENER + MEJORAR | apoyo | Permiso de circulación temporal: qué es y cómo pedirlo |
| 28 | `/exoneracion-de-impuestos-vehiculares/` | MANTENER + MEJORAR | apoyo | Exoneración de impuestos vehiculares en Ecuador |
| 29 | `/cambio-de-servicio-vehicular/` | MANTENER + MEJORAR | apoyo | Cambio de servicio vehicular: de particular a comercial |
| 30 | `/duplicado-de-matricula-vehicular/` | MANTENER + MEJORAR | apoyo | Duplicado de matrícula vehicular: cómo obtenerlo |
| 31 | `/baja-vehiculo/` | MANTENER + MEJORAR | apoyo | Baja de un vehículo en Ecuador: requisitos y pasos |
| 32 | `/pago-matricula-linea/` | MANTENER + MEJORAR | apoyo | Pago de matrícula en línea en Ecuador: guía segura |
| 33 | `/consulta-multas-transito/` | MANTENER + MEJORAR | apoyo | Consulta de multas de tránsito por placa en Ecuador |
| 34 | `/manual-paso-a-paso/` | MANTENER + MEJORAR | apoyo | Manual paso a paso: matricular tu vehículo en Ecuador |
| 35 | `/tramites-vehiculares/` | NUEVA | hub | Trámites vehiculares en Ecuador: índice completo |
| 36 | `/matriculacion-por-ciudad/` | NUEVA | hub | Matriculación vehicular por ciudad en Ecuador |
| 37 | `/blog/` | MANTENER | hub | Novedades de matriculación vehicular en Ecuador |
| 38 | `/formatos-descargables/` | MANTENER | hub | Formatos y modelos para trámites vehiculares |
| 39 | `/glosario-matriculacion-vehicular/` | NUEVA | hub | Glosario de matriculación vehicular en Ecuador |
| 40 | `/fuentes-oficiales-ecuador/` | NUEVA | confianza | Portales oficiales de tránsito y matriculación en Ecuador |
| 41 | `/sobre-nosotros/` | NUEVA | confianza | Sobre este sitio | Matriculación Vehicular Ecuador |
| 42 | `/metodologia-editorial/` | NUEVA | confianza | Metodología editorial | Matriculación Vehicular |
| 43 | `/contacto/` | MANTENER | confianza | Contacto | Matriculación Vehicular Ecuador |
| 44 | `/politica-de-privacidad/` | MANTENER | confianza | Política de privacidad | Matriculación Vehicular |
| 45 | `/politica-de-cookies/` | MANTENER | confianza | Política de cookies | Matriculación Vehicular |
| 46 | `/aviso-legal/` | MANTENER | confianza | Aviso legal | Matriculación Vehicular Ecuador |

Además: `404.html` (técnica, `noindex`).

Notas: **Ambato** y **Riobamba** se mantienen (Riobamba fue la única con clics en 2026); si no se consiguen datos locales verificables en el primer mes, la alternativa es fusionarlas en `/matriculacion-por-ciudad/` con 301.

## 8. Orden de trabajo recomendado

1. **Sprint 1:** calendario 2026 (con selector de dígito), valor a pagar, revisión técnica de Quito, multas, Riobamba/Ambato/Cuenca con datos locales.
2. **Sprint 2:** pilares que absorben tráfico existente (anual, propietario, características, nuevos).
3. **Sprint 3:** CUV, SPPAT, eléctricos, rebajas, bloqueo, turnos, moto.
4. **Sprint 4:** páginas de confianza y hubs.
5. **Sprint 5:** redirecciones y poda de los 180 posts antiguos.
6. **Sprint 6:** migración estática, DNS, Search Console, Bing, IndexNow.

## 9. Contenido de las páginas

Cada bloque a continuación es la **fuente real** del sitio: se publica tal cual lo lee `build.py`. Si editas aquí, vuelve a ejecutar el build.

<!-- PAGE:START slug=index -->
---
title: "Matriculación vehicular en Ecuador 2026: guía clara"
description: "Calendario por último dígito de placa, valor a pagar, revisión técnica, multas y trámites vehiculares en Ecuador, con enlaces a los portales oficiales."
h1: "Matriculación vehicular en Ecuador: calendario, costos y trámites"
short: "Inicio"
type: hub
schema: WebPage
updated: 2026-10-27
lead: "Encuentra tu mes de matriculación, cuánto pagar, dónde hacer la revisión técnica y qué trámite necesitas. Guías en lenguaje simple y siempre con el portal oficial a mano."
ctas:
  - {t: "Ver mi mes de matriculación", u: "/calendario-matriculacion-vehicular/"}
  - {t: "Calcular cuánto pagar", u: "/valor-a-pagar-matricula/", style: "secondary"}
related: [revision-tecnica-vehicular, multas-por-no-matricular-vehiculo, certificado-unico-vehicular, matriculacion-por-ciudad]
faq:
  - q: "¿Este sitio es oficial?"
    a: "No. Es una guía informativa independiente. Los pagos y trámites se hacen únicamente en los portales de la ANT, el SRI y los municipios que tienen la competencia. Te enlazamos a cada uno en la página [Portales oficiales](/fuentes-oficiales-ecuador/)."
  - q: "¿Cómo sé en qué mes matriculo mi vehículo?"
    a: "Depende del último dígito de la placa. El 1 matricula en febrero, el 2 en marzo y así hasta el 9 en octubre y el 0 en noviembre. Diciembre queda para los rezagados, con recargos."
  - q: "¿Qué pasa si me atraso en la matriculación?"
    a: "Generas recargos y puedes recibir una multa si circulas sin matrícula vigente. Lo explicamos con detalle en [multas por no matricular](/multas-por-no-matricular-vehiculo/)."
---
## Empieza por lo que necesitas hoy

Casi todas las visitas a este sitio tienen una sola pregunta: *¿cuándo y cuánto debo pagar?* Por eso lo primero es una herramienta de dos clics. Elige el último dígito de tu placa y te decimos qué mes te toca.

{{TOOL:digito}}

Si ya sabes tu mes, el siguiente paso es [calcular el valor a pagar](/valor-a-pagar-matricula/): la matrícula no es un solo cobro, sino la suma de varios rubros (impuesto, tasas, seguro obligatorio y, si corresponde, revisión técnica y multas pendientes).

## ¿Qué trámite necesitas?

Elige la situación que más se parece a la tuya:

{{TOOL:arbol}}

## Calendario de matriculación en una mirada

| Último dígito de la placa | Mes de matriculación |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

Diciembre se reserva para quienes no matricularon en su mes y pagan con recargos. La fecha límite es el último día del mes que te corresponde, aunque la autoridad puede publicar ampliaciones: revisa siempre la versión vigente en la [página del calendario](/calendario-matriculacion-vehicular/).

## Lo que debes tener claro antes de pagar

- **Matricular no es solo pagar la tasa.** Primero se consultan y cancelan multas, luego se paga el impuesto a la propiedad del vehículo y el SPPAT, y en la mayoría de ciudades se debe aprobar la [revisión técnica vehicular](/revision-tecnica-vehicular/).
- **Los valores cambian.** Dependen del avalúo del vehículo, el cilindraje, el tipo de servicio y la ciudad. Por eso en este sitio los montos aparecen siempre como referencia con fecha de revisión.
- **Un vehículo bloqueado no se matricula.** Si tiene una prohibición de enajenar o multas, primero toca el [desbloqueo](/bloqueo-vehicular-desbloqueo/).
- **Cada ciudad tiene sus propias reglas de revisión.** Consulta la guía de tu ciudad en [matriculación por ciudad](/matriculacion-por-ciudad/).

## Guías que más se consultan

1. [Valor a pagar de la matrícula](/valor-a-pagar-matricula/): qué rubros componen el total.
2. [Revisión técnica vehicular](/revision-tecnica-vehicular/): cuándo, dónde y qué se revisa.
3. [Multas por no matricular](/multas-por-no-matricular-vehiculo/): sanciones y cómo evitarlas.
4. [Cambio de propietario](/cambio-de-propietario-vehicular/): pasos y costos al comprar o vender.
5. [Certificado Único Vehicular](/certificado-unico-vehicular/): para qué sirve y cómo obtenerlo.
6. [Matrícula de motos](/matricula-moto/): particularidades para motocicletas.

## Cómo trabajamos

Cada guía cita la fuente oficial, indica la fecha de actualización y marca los montos que debes confirmar. Si encuentras un dato desactualizado, escríbenos desde la página de [contacto](/contacto/). Puedes conocer el método completo en [metodología editorial](/metodologia-editorial/).

Todos los trámites están organizados en [trámites vehiculares](/tramites-vehiculares/), y si buscas un término técnico (SPPAT, avalúo, CUV, RTV), el [glosario](/glosario-matriculacion-vehicular/) los explica en una línea.
<!-- PAGE:END -->

<!-- PAGE:START slug=calendario-matriculacion-vehicular -->
---
title: "Calendario de matriculación vehicular Ecuador 2026"
description: "Mes de matriculación según el último dígito de la placa en Ecuador: del 1 (febrero) al 0 (noviembre), plazos, recargos y qué hacer si te atrasaste."
h1: "Calendario de matriculación vehicular en Ecuador 2026"
short: "Calendario 2026"
type: pilar
schema: Article
updated: 2026-10-27
quick: "El mes lo define el último dígito de tu placa: 1 febrero, 2 marzo, 3 abril, 4 mayo, 5 junio, 6 julio, 7 agosto, 8 septiembre, 9 octubre y 0 noviembre. Diciembre es para rezagados, con recargos."
related: [valor-a-pagar-matricula, multas-por-no-matricular-vehiculo, revision-tecnica-vehicular, turno-matriculacion-vehicular, matriculacion-por-ciudad]
sources:
  - {t: "Agencia Nacional de Tránsito (ANT)", u: "https://www.ant.gob.ec"}
  - {t: "Servicio de Rentas Internas (SRI)", u: "https://www.sri.gob.ec"}
  - {t: "Agencia Metropolitana de Tránsito de Quito (AMT)", u: "https://www.amt.gob.ec"}
verify:
  - "Calendario 2026 por dígito: confirmar contra la resolución vigente de la ANT y las variantes de AMT, ATM y EMOV EP."
  - "Estado de plazos y posible ampliación de diciembre: confirmar en el portal oficial antes de publicar."
faq:
  - q: "Mi placa termina en 0, ¿cuándo matriculo?"
    a: "En noviembre. Es el último mes del calendario ordinario; si lo dejas pasar, solo queda diciembre con recargos."
  - q: "¿Se puede matricular antes de mi mes?"
    a: "En general los pagos se habilitan al abrir el periodo del dígito correspondiente. Revisa en el portal si tu vehículo aparece como disponible para pago antes de ir."
  - q: "¿Qué dígito cuenta si mi placa tiene letras?"
    a: "El último carácter numérico de la placa. En una placa como ABC-1234, el dígito que decide es el 4."
  - q: "¿Las motos siguen el mismo calendario?"
    a: "Sí, también se organizan por el último dígito de la placa. Revisa los detalles en [matrícula de motos](/matricula-moto/)."
  - q: "Estoy atrasado, ¿qué hago primero?"
    a: "Consulta el valor con recargos en el portal que corresponde a tu ciudad, cancela multas pendientes y agenda la revisión técnica si te la piden. La guía de [multas por no matricular](/multas-por-no-matricular-vehiculo/) explica el orden."
---
## Calcula tu mes en segundos

Elige el último dígito de tu placa. Si tu placa es **PBA-2849**, el dígito que cuenta es el **9**.

{{TOOL:digito}}

## Tabla completa del calendario

| Último dígito | Mes de matriculación | Fecha límite habitual |
|---|---|---|
| 1 | Febrero | Último día de febrero |
| 2 | Marzo | 31 de marzo |
| 3 | Abril | 30 de abril |
| 4 | Mayo | 31 de mayo |
| 5 | Junio | 30 de junio |
| 6 | Julio | 31 de julio |
| 7 | Agosto | 31 de agosto |
| 8 | Septiembre | 30 de septiembre |
| 9 | Octubre | 31 de octubre |
| 0 | Noviembre | 30 de noviembre |
| Rezagados | Diciembre | Con recargos |

La fecha límite es el último día del mes asignado. Cuando una autoridad amplía plazos lo hace mediante resolución; si eso ocurre, el portal oficial es la única fuente válida.

## Situación al 27 de octubre de 2026

- **Dígitos 1 al 8:** su mes ya pasó. Quien no matriculó está en mora y paga con recargos.
- **Dígito 9:** octubre es su mes y cierra el 31 de octubre. Si aún no has pagado, hazlo esta semana.
- **Dígito 0:** noviembre empieza en pocos días. Conviene adelantar la revisión técnica y consultar multas ahora.

## Qué se paga y en qué orden

La matriculación se concreta cuando todo está al día. El orden más práctico es:

1. **Consultar multas y deudas** del vehículo ([consulta de multas](/consulta-multas-transito/)).
2. **Aprobar la revisión técnica** en tu ciudad, si es obligatoria ([revisión técnica](/revision-tecnica-vehicular/)).
3. **Pagar el total** de la matrícula en el canal oficial ([pago en línea](/pago-matricula-linea/)).
4. **Retirar o descargar** la matrícula y el adhesivo según el procedimiento de tu ciudad.

El detalle de cada rubro está en [valor a pagar de la matrícula](/valor-a-pagar-matricula/).

## Calendario por ciudad: no siempre es idéntico

El mes se define a nivel nacional por el dígito, pero los municipios que gestionan la matriculación en su territorio (Quito, Guayaquil, Cuenca, entre otros) pueden tener sus propios canales, turnos y requisitos de revisión. En Quito, por ejemplo, desde febrero de 2026 la revisión técnica y la matriculación se coordinan en un proceso unificado según lo informado por la prensa y la autoridad municipal. Consulta tu caso:

- [Matriculación en Quito](/matriculacion-vehicular-quito/)
- [Matriculación en Guayaquil](/matriculacion-vehicular-guayaquil/)
- [Matriculación en Cuenca](/matriculacion-vehicular-cuenca/)
- [Otras ciudades](/matriculacion-por-ciudad/)

## Si te atrasaste

Pasarse del mes no cancela el derecho a matricular, pero sí cambia el costo y el riesgo:

- Se aplican **recargos** por mora sobre los rubros que los contemplan.
- Circular sin matrícula vigente es una **infracción**; detalles en [multas por no matricular](/multas-por-no-matricular-vehiculo/).
- Puedes quedar con **bloqueo** si acumulas deudas que impidan trámites ([desbloqueo vehicular](/bloqueo-vehicular-desbloqueo/)).

La recomendación es no esperar a diciembre: ese mes concentra a los rezagados y los canales se saturan.

## Casos particulares

**Vehículo recién comprado.** Si es nuevo, su primera matrícula sigue otro proceso: [matriculación de vehículos nuevos](/matriculacion-de-vehiculos-nuevos/). Si es usado, primero se hace el [cambio de propietario](/cambio-de-propietario-vehicular/) y después se matricula en el mes del dígito.

**Vehículo importado.** Cumple un proceso aduanero previo; consulta [vehículos importados](/matriculacion-de-vehiculos-importados/).

**Vehículos eléctricos.** Tienen beneficios tributarios que cambian el valor, pero el calendario es el mismo: [eléctricos y exoneración](/vehiculos-electricos-exoneracion-matricula/).

**Adultos mayores y personas con discapacidad.** Pueden acceder a rebajas o exoneraciones sobre el impuesto: [rebaja de matrícula](/rebaja-matricula-adultos-mayores-discapacidad/).

## Consejos para no tener sorpresas

- Revisa tu mes **con dos meses de anticipación**: la revisión técnica y los turnos se llenan.
- Verifica tu **correo y teléfono** registrados en el sistema para recibir avisos.
- Guarda siempre el **comprobante de pago** y la matrícula digital.
- Desconfía de gestores que prometen "ahorrar" el trámite: todo se hace por canales oficiales.

## Preguntas que más recibimos sobre fechas

**¿La fecha cambia cada año?** El esquema por dígito se mantiene, pero cada año se publica el calendario y puede haber ajustes de plazos o formas de pago. Este sitio indica la fecha de revisión en la parte superior de la página.

**¿Y si mi mes cayó en feriado?** El plazo corre hasta el último día del mes, no hasta una fecha puntual; si el último día es inhábil, confirma en el portal si se extiende.

**¿Puedo pagar en un banco?** Depende del canal habilitado para tu ciudad y año. Mira [pago en línea](/pago-matricula-linea/) y confirma las entidades autorizadas.
<!-- PAGE:END -->

<!-- PAGE:START slug=valor-a-pagar-matricula -->
---
title: "Valor a pagar de la matrícula vehicular en Ecuador"
description: "De qué se compone el total de la matrícula en Ecuador: impuesto, tasas, SPPAT, revisión técnica y multas. Cómo estimarlo y dónde consultarlo."
h1: "¿Cuánto se paga por la matrícula vehicular en Ecuador?"
short: "Valor a pagar"
type: pilar
schema: Article
updated: 2026-10-27
quick: "No hay un valor único. El total suma el impuesto a la propiedad del vehículo, el impuesto ambiental, el SPPAT, las tasas de matriculación y revisión técnica, y las multas o recargos pendientes. Consulta tu monto exacto en el portal del SRI o de tu municipio."
related: [calendario-matriculacion-vehicular, sppat, revision-tecnica-vehicular, multas-por-no-matricular-vehiculo, rebaja-matricula-adultos-mayores-discapacidad, pago-matricula-linea]
sources:
  - {t: "SRI: impuesto a la propiedad de vehículos motorizados", u: "https://www.sri.gob.ec"}
  - {t: "Agencia Nacional de Tránsito (ANT)", u: "https://www.ant.gob.ec"}
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
verify:
  - "Tabla progresiva del impuesto a la propiedad por avalúo: confirmar rangos y valores vigentes con el SRI."
  - "Valor del SPPAT por clase de vehículo: confirmar tarifa vigente."
  - "Valor de tasas de matriculación ANT/GAD y de RTV por ciudad: confirmar."
faq:
  - q: "¿Cuánto cuesta matricular un auto particular?"
    a: "Depende del avalúo, cilindraje y ciudad, por lo que no existe una cifra única. Un vehículo de bajo avalúo puede pagar poco; uno de avalúo alto, bastante más. Calcula tu caso con la consulta del SRI."
  - q: "¿Dónde consulto el valor exacto?"
    a: "En el portal del SRI (impuesto a la propiedad vehicular) y en el canal de matriculación de tu municipio o de la ANT. El total que ves al pagar es el único valor definitivo."
  - q: "¿El seguro obligatorio es opcional?"
    a: "No. El SPPAT es obligatorio y forma parte del pago de matrícula. Más detalles en [qué es el SPPAT](/sppat/)."
  - q: "¿Por qué pago más si me atrasé?"
    a: "Porque se suman recargos por mora y, si hubo infracciones, multas. El valor base no cambia, pero el total sí."
---
## La respuesta corta

Cuando alguien pregunta «¿cuánto cuesta la matrícula?», la respuesta depende de cuatro cosas: **el avalúo del vehículo**, **su cilindraje y antigüedad**, **el tipo de servicio** (particular, comercial, público) y **la ciudad donde matriculas**. Por eso quienes comparan montos en foros llegan a cifras tan distintas y todas pueden ser correctas.

Lo que sí es igual para todos es la estructura. A continuación está cada componente, quién lo cobra y cómo verificar tu monto.

## Los componentes del total

| Rubro | Quién lo cobra | De qué depende |
|---|---|---|
| Impuesto a la propiedad de vehículos motorizados | SRI | Avalúo del vehículo (tabla progresiva) |
| Impuesto ambiental a la contaminación vehicular | SRI | Cilindraje y antigüedad |
| SPPAT (seguro obligatorio de accidentes) | SPPAT | Clase y uso del vehículo |
| Tasa de matriculación | ANT o municipio | Tipo de vehículo y servicio |
| Revisión técnica vehicular y adhesivo | Municipio o centro autorizado | Ciudad y clase de vehículo |
| Multas pendientes | ANT, AMT, ATM, EMOV u otro | Infracciones registradas |
| Recargos por mora | Según el rubro | Meses de atraso |

### Impuesto a la propiedad del vehículo

Lo calcula el SRI sobre el **avalúo** del vehículo, aplicando una tabla progresiva: cuanto mayor el avalúo, mayor el impuesto. Para vehículos de menor valor la carga es pequeña, y existen exoneraciones y rebajas para ciertos grupos; las revisamos en [exoneración de impuestos vehiculares](/exoneracion-de-impuestos-vehiculares/) y en [rebaja para adultos mayores y personas con discapacidad](/rebaja-matricula-adultos-mayores-discapacidad/).

### Impuesto ambiental

Se aplica a vehículos de combustión según cilindraje y se ajusta por antigüedad. Los eléctricos tienen un tratamiento distinto, explicado en [vehículos eléctricos](/vehiculos-electricos-exoneracion-matricula/).

### SPPAT

Es el seguro público obligatorio de accidentes de tránsito. Sin él no se completa el proceso. Lo explicamos en [qué es el SPPAT](/sppat/).

### Tasas de matriculación y revisión técnica

La tasa depende de la entidad que emite la matrícula en tu territorio. La revisión técnica tiene una tarifa variable y un adhesivo; en Quito, el valor oficial del adhesivo es de USD 5. Las tarifas por ciudad están en [revisión técnica vehicular](/revision-tecnica-vehicular/).

### Multas y recargos

Antes de pagar la matrícula deben estar canceladas las multas registradas. Consúltalas en [consulta de multas de tránsito](/consulta-multas-transito/). Los recargos por mora se explican en [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Cómo estimar tu valor paso a paso

1. **Ubica tu avalúo.** Aparece en la consulta de impuesto vehicular del SRI con tu placa.
2. **Revisa el impuesto de tu año.** El sistema muestra el valor del impuesto a la propiedad y el ambiental.
3. **Suma SPPAT y tasas.** Se muestran en el estado de cuenta del canal de pago.
4. **Agrega la revisión técnica** si aún no la tienes aprobada.
5. **Descuenta beneficios** si calificas (adulto mayor, discapacidad, vehículo eléctrico).
6. **Verifica multas.** Si hay deudas, súmalas al presupuesto.

## Ejemplo de lectura de un estado de cuenta

Para entender la estructura sin dar cifras que cambian cada año, imagina el estado de cuenta de un auto particular: aparece una línea de «impuesto a la propiedad», otra de «impuesto ambiental», una de «SPPAT», una de «tasas» y, si corresponde, «multas» y «recargos». Cada línea tiene su propio concepto de pago. El total a depositar es la suma, y la matrícula se emite cuando todas las líneas están canceladas.

## Cómo se paga

Los canales dependen de la ciudad: portales en línea, entidades financieras autorizadas o ventanillas del municipio. Los pasos y las precauciones están en [pago de matrícula en línea](/pago-matricula-linea/). Si necesitas fecha, mira el [calendario](/calendario-matriculacion-vehicular/).

## Errores comunes que encarecen el trámite

- **Dejarlo para diciembre.** Se acumulan recargos y se saturan los canales.
- **No consultar multas antes.** El sistema bloquea el pago hasta que se cancelan.
- **Pagar por intermediarios.** Comisiones innecesarias y riesgo de fraude.
- **No aplicar beneficios.** Muchos adultos mayores no reclaman la rebaja a la que tienen derecho.
- **Confundir el avalúo.** Si el avalúo registrado es incorrecto, el impuesto también lo será; se puede solicitar corrección al SRI.

## Qué pasa si el valor te parece incorrecto

Primero compara con la consulta del SRI y la del municipio. Si hay diferencias, revisa si el vehículo tiene datos desactualizados (cilindraje, año, clase). Los cambios de características se gestionan en [cambio de características del vehículo](/cambio-de-caracteristicas-del-vehiculo/). Si persiste, presenta un reclamo en el canal oficial del rubro cuestionado.

## Resumen para llevar

El valor de la matrícula no es una tarifa, es una suma de rubros con dueños distintos. Entiende la estructura, consulta tu estado de cuenta y paga solo por canales oficiales. Verifica fecha de revisión de esta página: los montos y tablas cambian y aquí los tratamos como referencia.
<!-- PAGE:END -->

<!-- PAGE:START slug=multas-por-no-matricular-vehiculo -->
---
title: "Multas por no matricular el vehículo en Ecuador"
description: "Qué sanciones y recargos se aplican si no matriculas tu vehículo a tiempo en Ecuador, cómo consultarlas, pagarlas y evitar el bloqueo."
h1: "Multas por no matricular el vehículo en Ecuador"
short: "Multas por no matricular"
type: pilar
schema: Article
updated: 2026-10-27
quick: "Circular sin matrícula vigente es una infracción de tránsito y la mora genera recargos. El monto exacto se calcula sobre el Salario Básico Unificado y puede variar; consulta tus multas con la placa en el portal oficial antes de pagar."
related: [calendario-matriculacion-vehicular, consulta-multas-transito, bloqueo-vehicular-desbloqueo, valor-a-pagar-matricula, turno-matriculacion-vehicular]
sources:
  - {t: "Agencia Nacional de Tránsito (ANT)", u: "https://www.ant.gob.ec"}
  - {t: "Servicio de Rentas Internas (SRI)", u: "https://www.sri.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Monto de la multa por no matricular y por circular sin placas (porcentaje del SBU 2026): confirmar en normativa vigente (COIP y resoluciones)."
  - "Recargos por mora en matrícula: confirmar mecánica de cálculo con ANT/SRI."
faq:
  - q: "¿Me multan automáticamente si no matriculo?"
    a: "El atraso genera recargos en el sistema. La multa de tránsito se produce cuando la autoridad detecta que circulas sin matrícula vigente (control en vía o por cámaras, según el caso)."
  - q: "¿Puedo matricular aunque tenga multas?"
    a: "No. El sistema exige cancelar las multas registradas antes de completar la matrícula."
  - q: "¿Las multas prescriben?"
    a: "Existen reglas de prescripción, pero no conviene contar con ellas. Consulta el estado de tus multas en el portal y, si crees que prescribieron, solicita la verificación formal."
  - q: "¿Qué hago si me multaron por algo que no cometí?"
    a: "Puedes impugnar dentro de los plazos legales ante la autoridad que emitió la sanción. Guarda fotos, fechas y comprobantes."
---
## Dos cosas distintas: recargo y multa

Mucha confusión nace de mezclar dos conceptos:

- **Recargo por mora:** se suma al valor de la matrícula cuando pagas fuera de tu mes. Es un costo administrativo por el atraso.
- **Multa de tránsito:** es una sanción por una infracción, como **circular con matrícula vencida** o sin placas. La impone la autoridad de control.

Pagar a tiempo evita ambos. Pagar tarde casi siempre genera el primero, y el segundo aparece si te controlan en la vía.

## Qué infracciones se relacionan con la matrícula

| Situación | Tipo de problema |
|---|---|
| Matrícula vencida | Infracción por circular sin documento habilitante vigente |
| Circular sin placas o con placas ilegibles | Infracción distinta, con sanción propia |
| No haber aprobado la revisión técnica cuando es obligatoria | Impide matricular y puede sancionarse |
| Manipular o falsificar documentos | Delito, no solo infracción |

Los montos se expresan como porcentaje del **Salario Básico Unificado (SBU)**, y por eso se actualizan cuando cambia el SBU. En este sitio los marcamos como referencia: antes de pagar, valida el monto en el portal oficial.

## Cuánto puede costar de forma orientativa

Las cifras que circulan en medios y trámites se mueven en rangos de decenas de dólares por infracción y pueden acumularse por cada año de atraso, con topes distintos para transporte público. Como estos valores dependen del SBU y de la norma vigente, no te damos una cifra nacional cerrada: consulta tu estado de cuenta con la placa.

Como referencia de 2026: en **Quito**, la AMT cita USD 25 por no cumplir la calendarización, USD 50 por no acudir o no aprobar en la convocatoria y USD 25 de recargo anual por no pagar la matrícula; en **Guayaquil**, la ATM aplica un recargo de USD 50 a particulares y USD 100 a públicos por retraso en el proceso completo. El tarifario nacional de la ANT también lista USD 25 como recargo anual por no cancelar la matrícula. Detalle en [Quito](/matriculacion-vehicular-quito/) y [Guayaquil](/matriculacion-vehicular-guayaquil/).

## Cómo consultar tus multas

1. Ingresa al portal oficial que corresponde a tu vehículo: ANT, o el de tu municipio si la ciudad gestiona el tránsito (Quito, Guayaquil, Cuenca).
2. Busca por **placa** (y, si lo pide, por cédula del propietario).
3. Revisa si hay multas **pendientes**, **pagadas** o **en impugnación**.
4. Descarga el comprobante o la hoja de detalle.

Para el paso a paso, mira [consulta de multas de tránsito](/consulta-multas-transito/).

## Cómo pagarlas

Las multas se cancelan por los canales habilitados por la entidad que las emitió. Algunas permiten pago en línea con tarjeta o a través de bancos autorizados. Conserva siempre el comprobante hasta que el sistema refleje el pago, algo que puede tardar unas horas.

## Cuándo una multa te bloquea

Si acumulas deudas o hay sanciones firmes sin pagar, el vehículo puede quedar impedido de realizar trámites: matrícula, traspaso, baja. Para liberarlo hay un procedimiento específico en [bloqueo vehicular y desbloqueo](/bloqueo-vehicular-desbloqueo/).

## Estrategia para evitar multas y recargos

1. **Anota tu mes** del [calendario](/calendario-matriculacion-vehicular/) y pon una alarma dos meses antes.
2. **Aprueba la revisión técnica** cuando abra tu periodo ([guía de revisión técnica](/revision-tecnica-vehicular/)).
3. **Consulta multas** antes de intentar pagar.
4. **Agenda turno** si tu ciudad lo exige ([turnos de matriculación](/turno-matriculacion-vehicular/)).
5. **Paga en tu mes** y guarda el comprobante.

## Si ya estás atrasado

No esperes a que te controlen. Lo más sensato es:

- Calcular el total con recargos ([valor a pagar](/valor-a-pagar-matricula/)).
- Pagar multas pendientes.
- Matricular de inmediato.
- Evitar circular sin matrícula mientras tanto: el riesgo de multa y de retención del vehículo no compensa el ahorro.

## Casos frecuentes

**Compré un vehículo usado con matrícula vencida.** Las deudas siguen al vehículo. Antes de comprar, pide un [Certificado Único Vehicular](/certificado-unico-vehicular/) para ver multas y gravámenes.

**Vendí mi vehículo y siguen llegando multas.** Si no hiciste el [cambio de propietario](/cambio-de-propietario-vehicular/), legalmente sigues figurando como dueño. Regulariza el traspaso para cortar la responsabilidad.

**El vehículo no se usa.** Si no piensas circular, evalúa la [baja del vehículo](/baja-vehiculo/) en lugar de acumular mora.

**Mi vehículo está en otra ciudad.** La matrícula se gestiona según el registro del vehículo, no según donde estás. Revisa la guía de [matriculación por ciudad](/matriculacion-por-ciudad/).

## Mitos que cuestan dinero

- «Si no circulo, no pasa nada»: el recargo y la deuda igual corren mientras el vehículo esté registrado.
- «Pago la multa y ya queda matriculado»: son trámites separados.
- «Un gestor lo arregla más barato»: los costos oficiales son los mismos; el gestor solo suma comisión.

## Resumen

Evitar multas por no matricular es cuestión de calendario y de consultar a tiempo. Si ya te pasaste, actúa rápido y por canales oficiales. Los montos exactos dependen del SBU y de la norma vigente: valídalos siempre en el portal antes de pagar.
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-anual-vehicular -->
---
title: "Matriculación anual vehicular en Ecuador: guía 2026"
description: "Guía de matriculación anual en Ecuador: requisitos, pasos, orden de pagos, revisión técnica y qué hacer según tu situación."
h1: "Matriculación anual vehicular en Ecuador: requisitos y pasos"
short: "Matriculación anual"
type: pilar
schema: Article
updated: 2026-10-27
quick: "Para matricular cada año: consulta multas, aprueba la revisión técnica si te corresponde, paga impuestos, SPPAT y tasas en el canal oficial de tu ciudad, y descarga o retira la matrícula. Tu mes depende del último dígito de la placa."
related: [calendario-matriculacion-vehicular, valor-a-pagar-matricula, revision-tecnica-vehicular, pago-matricula-linea, manual-paso-a-paso, turno-matriculacion-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
faq:
  - q: "¿Cada cuánto se matricula un vehículo?"
    a: "Cada año, en el mes que corresponde al último dígito de la placa."
  - q: "¿Necesito llevar documentos físicos?"
    a: "En la mayoría de trámites anuales basta la placa y el pago en línea; pueden pedirte cédula o autorización si actúa un tercero. Confirma en el canal de tu ciudad."
  - q: "¿La revisión técnica es obligatoria en todo el país?"
    a: "Se exige en las jurisdicciones que la tienen implementada, y con reglas propias de periodicidad. Mira [revisión técnica vehicular](/revision-tecnica-vehicular/)."
  - q: "¿Qué pasa si pierdo la matrícula?"
    a: "Puedes solicitar un duplicado; el procedimiento está en [duplicado de matrícula](/duplicado-de-matricula-vehicular/)."
  - q: "¿Puedo matricular un vehículo que no es mío?"
    a: "Sí, es posible pagar con la placa, pero la matrícula queda a nombre del propietario registrado. Si compraste el vehículo, primero haz el [cambio de propietario](/cambio-de-propietario-vehicular/)."
---
## Qué es la matriculación anual

La matrícula es el documento que habilita a un vehículo a circular. En Ecuador se renueva cada año y se cobra a través de varios rubros que se pagan juntos. El proceso se parece en todo el país, pero los canales (portales, turnos, centros de revisión) dependen de quién gestiona el tránsito en tu ciudad.

## Antes de empezar: tu checklist

- [ ] Sé cuál es mi **mes** según el último dígito de la placa ([calendario](/calendario-matriculacion-vehicular/)).
- [ ] Consulté si hay **multas** pendientes ([consulta de multas](/consulta-multas-transito/)).
- [ ] Verifiqué si mi ciudad exige **revisión técnica** y si la tengo aprobada ([RTV](/revision-tecnica-vehicular/)).
- [ ] Tengo a mano la **placa** y la cédula del propietario.
- [ ] Conozco el **total** estimado ([valor a pagar](/valor-a-pagar-matricula/)).

## Paso a paso

### 1. Consulta de deudas
Ingresa con la placa al portal oficial de tu jurisdicción. Debes ver el estado del vehículo: impuestos pendientes, multas y bloqueos. Si hay un bloqueo, resuélvelo primero ([desbloqueo](/bloqueo-vehicular-desbloqueo/)).

### 2. Revisión técnica vehicular
Si tu ciudad la exige, aprueba la revisión en un centro autorizado. Guarda el comprobante o el adhesivo. En algunas ciudades la RTV y la matrícula se coordinan en un solo proceso. Detalles por ciudad en [revisión técnica en Quito](/revision-tecnica-vehicular-quito/), [Guayaquil](/revision-tecnica-vehicular-guayaquil/) y [Cuenca](/revision-tecnica-vehicular-cuenca/).

### 3. Pago de rubros
Paga impuesto a la propiedad, impuesto ambiental, SPPAT y tasas. Algunos canales reúnen todo en un solo pago; otros separan impuesto (SRI) y tasa (ANT o municipio). La explicación de cada rubro está en [valor a pagar](/valor-a-pagar-matricula/) y los canales en [pago en línea](/pago-matricula-linea/).

### 4. Turno, si corresponde
Algunas ciudades piden agendar para retirar documentos o adhesivos: [turnos de matriculación](/turno-matriculacion-vehicular/).

### 5. Obtención de la matrícula
Descarga el documento digital o retíralo según el procedimiento. Verifica que los datos (placa, chasis, propietario) estén correctos.

## Requisitos habituales

| Requisito | Cuándo se pide |
|---|---|
| Placa del vehículo | Siempre |
| Cédula del propietario | Para identificar o autorizar |
| Comprobante de revisión técnica | Donde es obligatoria |
| Pago de SPPAT | Siempre (forma parte del total) |
| Autorización escrita | Si tramita un tercero |

## Situaciones que cambian el proceso

- **Vehículo nuevo:** la primera matrícula tiene su propio flujo ([vehículos nuevos](/matriculacion-de-vehiculos-nuevos/)).
- **Vehículo importado:** requiere cumplimiento aduanero previo ([importados](/matriculacion-de-vehiculos-importados/)).
- **Compraste un usado:** hazlo a tu nombre antes ([cambio de propietario](/cambio-de-propietario-vehicular/)).
- **Cambió el uso (de particular a comercial):** [cambio de servicio](/cambio-de-servicio-vehicular/).
- **Moto:** [matrícula de motos](/matricula-moto/).
- **Eléctrico:** [exoneración para eléctricos](/vehiculos-electricos-exoneracion-matricula/).
- **Adulto mayor o persona con discapacidad:** [rebajas](/rebaja-matricula-adultos-mayores-discapacidad/).

## Cuánto tiempo tarda

Si todo está al día, el pago se refleja en minutos u horas y puedes descargar la matrícula el mismo día en canales digitales. Con revisión técnica o turno presencial, calcula varios días hábiles de margen. Por eso conviene empezar antes de que termine tu mes.

## Qué pasa si me atraso

Se aplican recargos y puedes recibir multas por circular sin matrícula vigente. Lee [multas por no matricular](/multas-por-no-matricular-vehiculo/) y prioriza regularizar.

## Errores frecuentes

1. Intentar pagar sin consultar multas.
2. Dejar la revisión técnica para los últimos días.
3. Pagar a terceros no autorizados.
4. No verificar los datos del vehículo en el documento final.
5. No guardar el comprobante.

## Documentos y trámites relacionados

Si necesitas un resumen completo del vehículo antes de comprarlo o venderlo, el [Certificado Único Vehicular](/certificado-unico-vehicular/) reúne la información. Para trámites en línea paso a paso, revisa el [manual paso a paso](/manual-paso-a-paso/). Y si buscas formularios, mira [formatos descargables](/formatos-descargables/).

## Buenas prácticas para el próximo año

Crea un recordatorio anual con tu mes y los dos meses previos para revisión técnica. Guarda en una carpeta (digital) la última matrícula, el comprobante de SPPAT y el de revisión técnica. Y si piensas vender el vehículo, mantén todo al día: un vehículo sin deudas se vende más rápido y mejor.
<!-- PAGE:END -->

<!-- PAGE:START slug=revision-tecnica-vehicular -->
---
title: "Revisión técnica vehicular en Ecuador: guía 2026"
description: "Qué es la revisión técnica vehicular (RTV) en Ecuador, quién debe hacerla, qué se revisa, costos de referencia, segunda revisión y adhesivo."
h1: "Revisión técnica vehicular (RTV) en Ecuador: cómo funciona"
short: "Revisión técnica"
type: pilar
schema: Article
updated: 2026-10-27
quick: "La RTV es la inspección obligatoria que verifica el estado mecánico, de seguridad y de emisiones del vehículo. Se hace en centros autorizados de tu ciudad, tiene tarifa variable y un adhesivo (en Quito, USD 5). Si no apruebas, tienes un plazo para una segunda revisión."
related: [revision-tecnica-vehicular-quito, revision-tecnica-vehicular-guayaquil, revision-tecnica-vehicular-cuenca, matriculacion-anual-vehicular, valor-a-pagar-matricula]
sources:
  - {t: "AMT Quito: revisión técnica", u: "https://www.amt.gob.ec"}
  - {t: "ATM Guayaquil", u: "https://www.atm.gob.ec"}
  - {t: "EMOV EP Cuenca", u: "https://www.emov.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
verify:
  - "Tarifas RTV Quito 2026 tomadas de Primicias (fuente AMT); el portal de la AMT bloquea lecturas automáticas."
  - "Plazos de segunda revisión por ciudad: confirmar."
faq:
  - q: "¿La revisión técnica es obligatoria?"
    a: "Sí, en las jurisdicciones donde está implementada. Sin ella no se completa la matrícula en esas ciudades."
  - q: "¿Cuánto cuesta?"
    a: "La tarifa es variable según clase de vehículo y ciudad, más el adhesivo. En Quito el adhesivo cuesta USD 5. Mira la tabla de tu ciudad en las guías locales."
  - q: "¿Qué hago si reprobé?"
    a: "Corrige las observaciones y vuelve a un segundo control dentro del plazo que fija tu ciudad (en Quito, referencia de 45 días para la segunda revisión). Pasado ese plazo puedes tener que pagar de nuevo."
  - q: "¿Puedo hacerla en cualquier ciudad?"
    a: "Debes hacerla en los centros autorizados de la jurisdicción donde está registrado el vehículo o donde la autoridad lo permita. Confirma antes."
  - q: "¿Los vehículos nuevos la necesitan?"
    a: "Los vehículos nuevos suelen tener un periodo de exoneración en su primera matrícula. Revisa [vehículos nuevos](/matriculacion-de-vehiculos-nuevos/) y la regla de tu ciudad."
---
## Qué es la revisión técnica vehicular

La **revisión técnica vehicular (RTV)** es una inspección periódica que comprueba que el vehículo cumple condiciones mínimas de **seguridad**, **funcionamiento mecánico** y **emisiones contaminantes**. En Ecuador la gestionan los municipios o entidades autorizadas, por eso cada ciudad tiene sus tarifas, sus centros y sus fechas.

Para el conductor, la RTV importa por una razón práctica: en las ciudades donde es obligatoria, **sin RTV aprobada no puedes completar la matrícula**.

## Quién debe hacerla y cuándo

- **Vehículos particulares y comerciales** registrados en jurisdicciones con RTV obligatoria.
- **Periodicidad:** anual en general, con periodo de exoneración para vehículos nuevos que cada ciudad define.
- **Momento recomendado:** uno o dos meses antes de tu mes del [calendario](/calendario-matriculacion-vehicular/).

Hay ciudades donde la RTV y la matrícula se tramitan de forma integrada. En Quito, según la prensa con datos de la AMT (enero de 2026), el vehículo que aprueba la revisión se matricula automáticamente en el mismo centro; revisa la guía local para el procedimiento vigente.

## Qué se revisa

| Área | Ejemplos de control |
|---|---|
| Luces y señalización | Delanteras, posteriores, direccionales, freno |
| Frenos | Eficiencia y equilibrio |
| Dirección y suspensión | Holguras y desgaste |
| Neumáticos | Profundidad del dibujo y estado general |
| Emisiones | Gases en vehículos de combustión |
| Carrocería y seguridad | Cinturones, parabrisas, espejos |
| Identificación | Placa, chasis y motor coinciden con el registro |

Los parámetros exactos los fija la norma técnica vigente y varían por tipo de vehículo.

## Cuánto cuesta

La tarifa es **variable**: depende de la clase de vehículo (liviano, moto, taxi, carga) y de la ciudad. A eso se suma el **adhesivo**. En Quito, la hoja municipal oficial fija el adhesivo en **USD 5,00**. En Guayaquil y Cuenca hay tablas propias; las resumimos en sus guías:

Comparación de la **primera revisión de un liviano particular** en 2026, según fuentes de cada ciudad:

| Ciudad | Liviano (USD) | Adhesivo (USD) | Fuente |
|---|---|---|---|
| Quito | 31,56 | 5,00 | AMT vía Primicias; ficha municipal |
| Guayaquil | 29,87 | 3,90 | Tarifario ATM 2026 |
| Cuenca | Sin confirmar | 5,00 | EMOV EP |

El tarifario nacional de la ANT para los GAD fija una referencia de USD 27 para livianos y USD 5 para el adhesivo; las ciudades con tarifario propio pueden diferir.

- [Revisión técnica en Quito](/revision-tecnica-vehicular-quito/)
- [Revisión técnica en Guayaquil](/revision-tecnica-vehicular-guayaquil/)
- [Revisión técnica en Cuenca](/revision-tecnica-vehicular-cuenca/)

Los valores de referencia se confirman siempre en la fuente oficial de tu ciudad antes de pagar.

## Paso a paso

1. **Verifica** si tu vehículo debe pasar RTV este año y en qué centros.
2. **Agenda** el turno si el centro lo exige ([turnos](/turno-matriculacion-vehicular/)).
3. **Prepara el vehículo:** luces, llantas, frenos, nivel de fluidos, documentos.
4. **Acude** con la matrícula anterior o el número de placa y la cédula del propietario o autorizado.
5. **Paga** la tarifa y el adhesivo en el canal indicado.
6. **Recibe el resultado:** aprobado, aprobado con observaciones menores o rechazado.
7. **Si apruebas,** el resultado queda registrado y puedes continuar con la matrícula ([matriculación anual](/matriculacion-anual-vehicular/)).

## Qué hacer si no apruebas

Te entregan la lista de observaciones. Repara los puntos señalados y regresa para la **segunda revisión**, que suele tener costo reducido o nulo si la haces dentro del plazo que fija el municipio. En Quito la referencia es de 45 días; los controles siguientes tienen plazos más cortos (30 días en las siguientes revisiones). Si pasas el plazo, puedes tener que pagar nuevamente.

## Cómo preparar el vehículo para aprobar

- Cambia focos quemados y revisa que **todas las luces** funcionen.
- Revisa **neumáticos**: sin cortes, desgaste parejo y dibujo suficiente.
- Haz una **afinación** si el vehículo emite humo visible.
- Verifica **frenos** y nivel de líquidos.
- Comprueba que el **parabrisas** no tenga fisuras que obstruyan la visión.
- Limpia el vehículo: un número de chasis ilegible complica la identificación.
- Lleva documentos al día y sin multas pendientes ([consulta de multas](/consulta-multas-transito/)).

## Errores comunes

1. Ir a último momento y topar con filas o turnos agotados.
2. No llevar la identificación correcta.
3. Pagar a «tramitadores» fuera del centro.
4. Confundir el adhesivo de la RTV con la matrícula: son documentos distintos.
5. Olvidar corregir observaciones menores y reprobar por lo mismo.

## RTV y matrícula: cómo se conectan

La matrícula exige que el vehículo esté al día con deudas y, donde corresponde, con la RTV. Si tu mes está cerca y aún no tienes la revisión, empieza por ella. Para entender qué más compone el total, lee [valor a pagar](/valor-a-pagar-matricula/); para evitar sanciones, [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Preguntas sobre casos especiales

**Motos.** Tienen tarifas y procedimiento propios, ver [matrícula de motos](/matricula-moto/).

**Vehículos eléctricos.** Siguen las inspecciones de seguridad, aunque sin control de emisiones de escape: [eléctricos](/vehiculos-electricos-exoneracion-matricula/).

**Vehículo que cambia de ciudad.** El registro de jurisdicción determina dónde matriculas; consulta [matriculación por ciudad](/matriculacion-por-ciudad/).

**Importados recientes.** Suelen tener tratamiento propio en su primera matrícula: [importados](/matriculacion-de-vehiculos-importados/).
<!-- PAGE:END -->

<!-- PAGE:START slug=cambio-de-propietario-vehicular -->
---
title: "Cambio de propietario de vehículo en Ecuador"
description: "Cómo hacer el traspaso de un vehículo en Ecuador: requisitos, pasos, costos de referencia, plazos y errores que evitar al comprar o vender."
h1: "Cambio de propietario de un vehículo en Ecuador: requisitos, pasos y costos"
short: "Cambio de propietario"
type: pilar
schema: Article
updated: 2026-10-27
quick: "El traspaso se hace con el contrato de compraventa, el pago del impuesto por transferencia y el registro del cambio en el sistema de tránsito. Hazlo dentro del plazo legal para no seguir respondiendo por multas del vehículo."
related: [certificado-unico-vehicular, bloqueo-vehicular-desbloqueo, valor-a-pagar-matricula, multas-por-no-matricular-vehiculo, matriculacion-anual-vehicular, duplicado-de-matricula-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Costo del traspaso: 1% (SRI), valores de la tasa ANT y especie USD 22, plazo de 30 días y multa 5% SBU: confirmar con normativa vigente."
faq:
  - q: "¿Quién paga el traspaso?"
    a: "Por costumbre lo asume el comprador, pero es un acuerdo entre las partes. Déjalo escrito en el contrato."
  - q: "¿Cuánto tengo para hacer el traspaso?"
    a: "La norma fija un plazo corto desde la compra (referencia: 30 días). Pasado ese plazo pueden aplicarse sanciones. Confirma el plazo vigente."
  - q: "¿Puedo vender si hay multas?"
    a: "Puedes pactar la venta, pero el sistema no permitirá el traspaso hasta regularizar deudas y bloqueos. Mejor solucionarlo antes: [desbloqueo](/bloqueo-vehicular-desbloqueo/)."
  - q: "¿Qué pasa si vendí y el comprador no hizo el traspaso?"
    a: "Legalmente sigues apareciendo como propietario y pueden llegarte multas. Guarda el contrato y exige que se complete el trámite."
  - q: "¿Necesito presencia de ambos?"
    a: "Depende del canal. Si no pueden ir ambos, se usa autorización o poder según corresponda."
---
## Qué es el cambio de propietario

También llamado **traspaso** o **transferencia de dominio**, es el trámite que registra que un vehículo pasó de una persona a otra. Hasta que no se completa, la matrícula sigue a nombre del vendedor, aunque el vehículo físicamente lo use el comprador.

Hacerlo bien protege a ambas partes: el comprador adquiere la propiedad formal y el vendedor deja de responder por multas, accidentes o deudas posteriores.

## Antes de comprar: verifica el vehículo

1. **Pide un [Certificado Único Vehicular (CUV)](/certificado-unico-vehicular/)** o su consulta equivalente: revela gravámenes, bloqueos y datos oficiales.
2. **Consulta multas** por placa ([consulta de multas](/consulta-multas-transito/)).
3. **Comprueba que los datos coincidan:** chasis, motor, color y año deben coincidir con el vehículo y con la matrícula.
4. **Verifica que el vendedor sea el propietario** registrado.
5. **Pide el historial de matriculación** y las revisiones técnicas al día.

## Documentos habituales

| Documento | Quién lo aporta |
|---|---|
| Contrato de compraventa | Ambas partes |
| Cédula de comprador y vendedor | Ambas partes |
| Matrícula del vehículo | Vendedor |
| Comprobante de pago del impuesto por transferencia | Quien paga |
| Certificado de no tener bloqueos ni deudas | Vendedor |
| Autorización o poder (si actúa un tercero) | Quien delega |

## Paso a paso

### 1. Redacta el contrato de compraventa
Debe incluir datos de las partes, descripción del vehículo (placa, chasis, motor, marca, modelo, año, color), precio, forma de pago, fecha y quién asume los costos. Se puede reconocer firmas ante notario según el procedimiento que exija el canal.

### 2. Paga los impuestos y tasas
El traspaso causa un **impuesto de transferencia** que se calcula sobre el valor de la operación o el avalúo (referencia: 1% con los parámetros del SRI) y **tasas** de la entidad de tránsito. Estos montos se confirman con las tablas vigentes ([valor a pagar](/valor-a-pagar-matricula/) explica la lógica de rubros).

### 3. Registra el cambio
Se ingresa el trámite en el sistema de la ANT o de tu municipio; algunas ciudades lo hacen en línea con turno. Revisa [turnos de matriculación](/turno-matriculacion-vehicular/).

### 4. Obtén la matrícula a nombre del nuevo dueño
Con el traspaso registrado se actualiza el documento. Verifica los datos.

### 5. Matrícula del año
Si el traspaso coincide con tu mes, aprovecha para completar la [matriculación anual](/matriculacion-anual-vehicular/).

## Plazos y sanciones

La norma establece un plazo corto para registrar el traspaso tras la compra. Si no lo cumples, puedes recibir una **sanción pecuniaria** (referencia: un porcentaje del SBU). Quien vendió debe protegerse: guarda el contrato y comprobantes de entrega.

## Costos de referencia

Los costos reales dependen del precio de venta, del avalúo y de la ciudad. Como estructura, piensa en tres bloques: impuesto de transferencia, tasa de trámite y especies o formularios. Verifica cada uno en el portal oficial porque cambian. No pagues a intermediarios que cobran «paquetes» sin detallar rubros.

Tasas de referencia 2026 para el traspaso de dominio: **USD 7,00** en el tarifario de la ANT y en Cuenca (más USD 22 de la especie de matrícula); **USD 13,23** en Guayaquil. No registrar el traspaso dentro de 30 días es infracción del artículo 392, numeral 13, del COIP. El impuesto por la transferencia depende del contrato y no está incluido en estas tasas.

## Cómo protegerte como vendedor

- **No entregues el vehículo sin contrato firmado** y sin comprobante de pago.
- **Acuerda por escrito la fecha** límite para el traspaso.
- **Toma nota** del kilometraje y estado en la entrega.
- Si el comprador no responde, **notifica** formalmente y consulta cómo reportar el vehículo vendido ante la autoridad.
- Sigue consultando que no aparezcan multas a tu nombre.

## Cómo protegerte como comprador

- **Paga contra documentos**, no antes.
- **Nunca compres un vehículo bloqueado** sin plan de desbloqueo.
- **Verifica la procedencia** y si hay prohibiciones de enajenar.
- **Haz el traspaso de inmediato**, no esperes a la matrícula.

## Casos especiales

**Herencia o donación.** Tienen requisitos distintos (escrituras, partición, exoneraciones). Consulta con la entidad de tránsito.

**Vehículo con prenda.** Si existe crédito prendario, se necesita el levantamiento de la prenda o la autorización de la entidad acreedora.

**Cambio de servicio al comprar.** Si pasas de particular a comercial, revisa [cambio de servicio](/cambio-de-servicio-vehicular/).

**Pérdida de la matrícula.** Tramita el [duplicado](/duplicado-de-matricula-vehicular/) antes del traspaso.

**Vehículo con multas antiguas.** Revisa [multas por no matricular](/multas-por-no-matricular-vehiculo/) para entender cómo afectan la operación.

## Checklist rápido

- [ ] CUV o consulta oficial sin bloqueos.
- [ ] Multas en cero.
- [ ] Contrato firmado y reconocido.
- [ ] Impuesto de transferencia pagado.
- [ ] Traspaso registrado dentro del plazo.
- [ ] Matrícula actualizada.
- [ ] Revisión técnica y matrícula anual al día.
<!-- PAGE:END -->

<!-- PAGE:START slug=cambio-de-caracteristicas-del-vehiculo -->
---
title: "Cambio de color, motor o carrocería de un vehículo"
description: "Cómo legalizar el cambio de color, motor o carrocería de tu vehículo en Ecuador: requisitos, pasos, inspección y costos de referencia."
h1: "Cambio de características del vehículo: color, motor y carrocería"
short: "Cambio de características"
type: pilar
schema: Article
updated: 2026-10-27
quick: "Si cambias color, motor, carrocería u otra característica registrada, debes actualizarlo en el sistema de tránsito con respaldo técnico y documentos. Sin el registro, el vehículo no coincide con la matrícula y puedes tener problemas en la revisión técnica, al vender o en un control."
related: [matriculacion-anual-vehicular, cambio-de-servicio-vehicular, revision-tecnica-vehicular, certificado-unico-vehicular, cambio-de-propietario-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
  - {t: "ATM Guayaquil", u: "https://www.atm.gob.ec"}
verify:
  - "Requisitos y costos exactos por tipo de cambio (color, motor, carrocería): confirmar con la entidad de tránsito de cada ciudad."
faq:
  - q: "¿Debo registrar el cambio de color?"
    a: "Sí. El color figura en la matrícula; si no lo actualizas, el vehículo no coincide con el documento."
  - q: "¿Puedo cambiar el motor y conservar la placa?"
    a: "Sí, pero el cambio debe registrarse con la factura del motor, la inspección y la declaración correspondiente."
  - q: "¿Necesito autorización para modificar la carrocería?"
    a: "Las modificaciones estructurales o de capacidad suelen requerir aprobación técnica previa. Pregunta antes de intervenir."
  - q: "¿Esto afecta el valor que pago?"
    a: "Puede afectarlo si cambia cilindraje, clase o servicio, porque varían impuestos y tasas."
---
## Por qué importa actualizar las características

La matrícula describe el vehículo con datos oficiales: marca, modelo, año, **color**, **motor**, **chasis**, clase, servicio. Si haces un cambio físico (pintura, motor, carrocería) y no lo registras, hay discrepancia entre el vehículo y el documento. Eso puede traerte:

- Rechazo en la [revisión técnica](/revision-tecnica-vehicular/) por falta de coincidencia.
- Dificultades al [vender](/cambio-de-propietario-vehicular/) o transferir.
- Posibles observaciones en controles en vía.
- Problemas con seguros ante un siniestro.

## Tipos de cambios más frecuentes

| Cambio | Qué suele pedirse |
|---|---|
| Color | Solicitud, factura o declaración de pintura, inspección de verificación |
| Motor | Factura del motor, documento de origen o importación, inspección y verificación del número |
| Carrocería | Aprobación técnica, factura del carrozado, inspección |
| Combustible (por ejemplo conversión a gas) | Certificado de homologación del taller y verificación |
| Capacidad o tipo de uso | Informe técnico y cambio de clase o servicio |

El listado exacto depende de la entidad que gestione el tránsito en tu ciudad.

## Paso a paso general

1. **Antes de intervenir**, consulta si el cambio requiere autorización previa.
2. **Conserva facturas** y documentos de origen de repuestos o motores.
3. **Haz el trabajo en un taller formal** que entregue comprobantes con datos del vehículo.
4. **Solicita el cambio** en el canal oficial (portal o ventanilla) y adjunta la documentación.
5. **Inspección:** el vehículo puede ser revisado para verificar números y cambios.
6. **Pago de tasas** del trámite.
7. **Actualización** de la matrícula con las nuevas características.

## Cambio de color en detalle

Es el trámite más sencillo. Normalmente:

- Presentas la solicitud con la placa y el nuevo color.
- Adjuntas factura o constancia del taller de pintura.
- Pasas por una verificación visual.
- Se actualiza el registro.

Si el cambio es parcial (franjas, publicidad), consulta si requiere registro.

## Cambio de motor en detalle

Es más delicado porque el número de motor es un identificador del vehículo. Debes demostrar el **origen legal** del motor nuevo: factura del vendedor, documento de importación si es el caso, y evitar motores sin procedencia clara, que pueden estar asociados a robos. La inspección verifica el nuevo número y la coherencia con el registro.

## Cambio de carrocería

Puede implicar cambio de clase o capacidad (por ejemplo, de camioneta a vehículo de carga). Esto repercute en tasas, impuestos y servicio. Revisa [cambio de servicio](/cambio-de-servicio-vehicular/) y [valor a pagar](/valor-a-pagar-matricula/) para entender el impacto.

## Costos y tiempos

Los costos incluyen tasas de trámite, posible inspección y los gastos del propio taller. Los tiempos varían de unos días a varias semanas según la ciudad y la complejidad. Consulta los valores oficiales antes de iniciar y no aceptes «paquetes» sin factura.

## Errores frecuentes

- **Cambiar el motor y no registrarlo.** Es de los motivos más comunes de problemas al vender.
- **Pintar sin informar.** Parece menor, pero genera discrepancias en la RTV.
- **No guardar facturas.** Sin respaldo, el trámite se detiene.
- **Usar piezas o motores de origen dudoso.** Riesgo legal y de seguridad.

## Relación con otros trámites

Si además vas a matricular, haz primero el cambio y luego la [matriculación anual](/matriculacion-anual-vehicular/). Si vas a vender, actualiza los datos antes del [traspaso](/cambio-de-propietario-vehicular/). Para verificar cómo figura hoy tu vehículo, solicita el [CUV](/certificado-unico-vehicular/).

## Recomendaciones

Antes de pintar o modificar, toma fotos del estado inicial y del número de chasis y motor. Pregunta a la entidad de tránsito qué documentos esperan para tu caso. Y si el vehículo tiene prenda o bloqueo, resuélvelo primero ([desbloqueo](/bloqueo-vehicular-desbloqueo/)).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-de-vehiculos-nuevos -->
---
title: "Matriculación de vehículos nuevos en Ecuador"
description: "Cómo se matricula un vehículo nuevo en Ecuador: documentos, pasos con el concesionario, pagos, placas y exoneración inicial de revisión técnica."
h1: "Matriculación de vehículos nuevos en Ecuador"
short: "Vehículos nuevos"
type: pilar
schema: Article
updated: 2026-10-27
quick: "El concesionario entrega la factura y documentos de origen; con ellos se registra el vehículo, se pagan impuestos, tasas y SPPAT, y se asignan placas. Muchas ciudades exoneran la revisión técnica en la primera matrícula."
related: [matriculacion-anual-vehicular, valor-a-pagar-matricula, sppat, vehiculos-electricos-exoneracion-matricula, duplicado-de-placas-vehiculares]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
verify:
  - "Duración de la exoneración de RTV para vehículos nuevos por ciudad: confirmar."
  - "Documentos exactos del concesionario/importador y tasa de placas: confirmar."
faq:
  - q: "¿Quién hace el trámite, yo o el concesionario?"
    a: "Muchos concesionarios gestionan la matrícula como servicio. Pregunta qué incluye y revisa los rubros que cobran."
  - q: "¿Cuándo recibo las placas?"
    a: "Tras completar el registro y pago, se asignan; los tiempos de entrega dependen de la ciudad y de la entidad."
  - q: "¿Pago revisión técnica en la primera matrícula?"
    a: "Normalmente no en el primer periodo, pero la regla depende de la ciudad. Confirma en la guía de [revisión técnica](/revision-tecnica-vehicular/)."
  - q: "¿El mes de matriculación se define por la placa nueva?"
    a: "Sí, por el último dígito de la placa asignada, mira el [calendario](/calendario-matriculacion-vehicular/)."
---
## Cómo es la primera matrícula

Comprar un vehículo nuevo implica un trámite inicial distinto al de la renovación anual. En lugar de renovar un registro existente, se **crea el registro** del vehículo, se **asignan placas** y se emiten los documentos de propiedad y circulación. Normalmente lo coordina el concesionario, pero conviene que entiendas cada paso para no pagar de más ni quedarte sin documentos.

## Documentos que necesitas

| Documento | Quién lo entrega |
|---|---|
| Factura de compra | Concesionario |
| Documento de origen del vehículo (para vehículos de fabricación o importación) | Concesionario o importador |
| Cédula del comprador | Comprador |
| Comprobantes de pago de impuestos y tasas | Según el canal |
| Contrato de financiamiento o reserva de dominio (si aplica) | Entidad financiera |

Verifica que los datos de la factura (chasis, motor, color, año) coincidan con el vehículo físico antes de firmar.

## Paso a paso

1. **Elige y paga el vehículo** con factura a tu nombre (o el de la empresa).
2. **Solicita los documentos de origen** y confirma qué gestiones incluye el concesionario.
3. **Registro del vehículo** en el sistema de tránsito de la jurisdicción.
4. **Pago de impuestos y tasas:** impuesto a la propiedad, ambiental si aplica, SPPAT y tasas de matriculación ([valor a pagar](/valor-a-pagar-matricula/)).
5. **Asignación de placas** y emisión de la matrícula ([placas](/duplicado-de-placas-vehiculares/) por si necesitas reposición luego).
6. **Registro de la entidad financiera**, si hay crédito con prenda.
7. **Entrega** con matrícula, placas y copias de comprobantes.

## Qué se paga

La estructura es la misma que en la renovación, con particularidades:

- **Impuesto a la propiedad** sobre el avalúo del vehículo nuevo.
- **Impuesto ambiental** si es de combustión.
- **SPPAT** desde la primera matrícula ([qué es](/sppat/)).
- **Tasas** de matriculación y placas.
- **Beneficios** para eléctricos u otros casos ([eléctricos](/vehiculos-electricos-exoneracion-matricula/), [exoneraciones](/exoneracion-de-impuestos-vehiculares/)).

## Revisión técnica en el primer periodo

Muchas jurisdicciones eximen al vehículo nuevo de la RTV durante un periodo inicial. Eso no significa que no deba hacerse después: cuando venza el beneficio, entra al ciclo normal ([RTV](/revision-tecnica-vehicular/)).

## Tu mes de renovación

Se define por el último dígito de la placa asignada. Anótalo desde el primer día en tu calendario ([calendario](/calendario-matriculacion-vehicular/)); la primera renovación llega rápido.

## Recomendaciones antes de recibir el vehículo

- Revisa que la **factura** tenga todos los datos y sea legible.
- Pide **desglose escrito** de lo que cobra el concesionario por el trámite.
- No aceptes entregas sin **placas o permiso de circulación temporal** ([permiso temporal](/permiso-de-circulacion-temporal/)).
- Guarda copias digitales de todos los documentos.

## Si el vehículo es importado

El proceso incluye cumplimiento aduanero y homologación; mira [vehículos importados](/matriculacion-de-vehiculos-importados/).

## Errores comunes

1. Firmar sin verificar chasis y motor contra el documento.
2. Pagar rubros duplicados al concesionario y al sistema.
3. Circular sin placas ni permiso.
4. No programar la primera renovación.

## Matrícula del vehículo nuevo si lo compras a crédito

Cuando financias la compra, la entidad financiera suele exigir que el vehículo quede con **prenda o reserva de dominio** a su favor. Esto aparece como una restricción en el sistema hasta que termines de pagar el crédito. Debes saber tres cosas:

1. La matrícula sale a tu nombre, pero el vehículo no podrá venderse ni darse de baja sin el levantamiento de la prenda.
2. Si el banco gestiona el trámite, pide copia de todos los comprobantes que pagues.
3. Al cancelar el crédito, solicita el documento de levantamiento y verifica que el sistema lo refleje ([bloqueo vehicular](/bloqueo-vehicular-desbloqueo/)).

## Después de la primera matrícula

Mantén un archivo con matrícula, factura, SPPAT y manual del vehículo. Si más adelante cambias el uso o el propietario, consulta [cambio de servicio](/cambio-de-servicio-vehicular/) y [cambio de propietario](/cambio-de-propietario-vehicular/). Para el ciclo normal, mira la [matriculación anual](/matriculacion-anual-vehicular/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-vehicular-quito -->
---
title: "Matriculación vehicular en Quito: pasos y requisitos"
description: "Cómo matricular tu vehículo en Quito: mes según placa, revisión y matrícula en el mismo centro, tarifas 2026, multas y centros de la AMT."
h1: "Matriculación vehicular en Quito"
short: "Quito"
type: local
parent: matriculacion-por-ciudad
schema: Article
updated: 2026-10-27
quick: "En Quito la AMT gestiona la matrícula. Si tu vehículo pasa la revisión técnica, se matricula en el mismo centro. En 2026 la revisión de un liviano cuesta USD 31,56 (primera revisión), el adhesivo USD 5 y la multa por no cumplir tu mes es de USD 25."
related: [revision-tecnica-vehicular-quito, calendario-matriculacion-vehicular, valor-a-pagar-matricula, multas-por-no-matricular-vehiculo, turno-matriculacion-vehicular]
sources:
  - {t: "Municipio de Quito: ficha de trámite RTV (GADDMQ-MO-AMT-39)", u: "https://pam.quito.gob.ec"}
  - {t: "Primicias: revisión vehicular 2026 en Quito", u: "https://www.primicias.ec"}
  - {t: "Quito Informa", u: "https://www.quitoinforma.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Valores de la tabla RTV 2026 provienen de Primicias (fuente AMT, ene 2026); el portal de la AMT bloquea lecturas automáticas y no se pudo contrastar directamente."
  - "Horarios de centros: la ficha municipal indica lun-vie 08:00-17:00 y sáb 08:00-12:00; la prensa de enero 2026 indicó otros horarios para el esquema con turno. Confirmar en la AMT."
faq:
  - q: "¿Quién gestiona la matrícula en Quito?"
    a: "La Agencia Metropolitana de Tránsito (AMT), en coordinación con el SRI para los impuestos y el SPPAT para el seguro obligatorio."
  - q: "¿Cuánto cuesta la revisión técnica de un auto liviano en Quito?"
    a: "En 2026, USD 31,56 la primera revisión y USD 15,80 la tercera, más USD 5 del adhesivo. La segunda es la corrección dentro del plazo."
  - q: "¿Cuánto es la multa por no matricular a tiempo en Quito?"
    a: "Según la AMT en 2026: USD 25 por no cumplir la calendarización, USD 50 si no acudes o no apruebas tras la convocatoria y USD 25 de recargo anual por no pagar la matrícula."
  - q: "¿Dónde me matriculo después de aprobar la revisión?"
    a: "En el mismo centro: el vehículo aprobado se matricula automáticamente y el permiso de circulación llega por correo electrónico."
  - q: "¿Cuántos días tengo para volver si no apruebo?"
    a: "Según la ficha municipal, hasta 45 días para la segunda revisión y 30 para la tercera y la cuarta, siempre dentro del periodo de convocatoria."
---
## Cómo funciona en Quito

Quito es una de las ciudades que gestionan el tránsito por su cuenta: la **Agencia Metropolitana de Tránsito (AMT)** es la entidad de referencia y el Municipio opera los centros de revisión técnica vehicular. Por eso tarifas, centros y multas pueden diferir de las de otras provincias, aunque el calendario por dígito de placa es el nacional.

En 2026 el trámite funciona así: llevas el vehículo al centro de revisión; si **aprueba**, queda matriculado en el mismo centro de forma automática y el permiso de circulación anual llega a tu correo electrónico. Si no aprueba, corriges las observaciones y regresas dentro del plazo. Es decir, la revisión técnica y la matrícula se encadenan en una sola visita cuando todo está en regla.

## Tu mes de matriculación

| Último dígito | Mes |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

Diciembre queda para los rezagados. En enero de 2026 la AMT atendió a quienes se habían quedado atrás en 2025 y a quienes quisieron adelantar su renovación. Más sobre mora en el [calendario nacional](/calendario-matriculacion-vehicular/).

**Caso 2026:** por el cierre temporal de la ANT y de su sistema AXIS 4.0, Quito Informa comunicó el 3 de marzo que los vehículos con placas terminadas en 1 y 2 podían empezar la revisión ese día, y que la placa 1 quedaba libre de la multa de USD 25 por calendarización. Es un ejemplo de por qué conviene revisar los avisos de la AMT antes de dar por perdido el plazo.

## Tarifas de revisión técnica en Quito (2026)

Valores en dólares, publicados por la prensa con datos de la AMT en enero de 2026. Detalle por categoría en la guía de [revisión técnica en Quito](/revision-tecnica-vehicular-quito/).

| Clase | Primera revisión | Tercera revisión |
|---|---|---|
| Livianos | 31,56 | 15,80 |
| Motos | 18,55 | 9,30 |
| Taxis | 21,40 | 10,70 |
| Buses | 42,00 | 21,00 |
| Pesados | 50,00 | 25,00 |

A eso se suman el **adhesivo (USD 5,00)** y el impuesto al rodaje, que se paga aparte según la ficha municipal.

## Multas y recargos en Quito

Según la AMT en 2026:

- **USD 25** por no cumplir con la calendarización (hacer el proceso fuera de tu mes).
- **USD 50** por no acudir a la convocatoria o no aprobar la revisión en ella.
- **USD 25** de recargo anual por no pagar la matrícula.

Antes de pagar, confirma si tu placa fue beneficiada con alguna extensión. Para la estructura general de sanciones, mira [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Paso a paso en Quito

1. **Consulta deudas y multas** con la AMT, el SRI y la ANT. La ficha municipal exige no tener deudas pendientes con esas entidades.
2. **Verifica tu mes** según el último dígito de la placa.
3. **Ve al centro de revisión** con cédula, matrícula original y el vehículo en buen estado ([turnos](/turno-matriculacion-vehicular/)).
4. **Paga la revisión, el adhesivo y el rodaje.**
5. **Si apruebas,** el vehículo se matricula en el centro y recibes el permiso por correo.
6. **Si no apruebas,** corrige y regresa dentro del plazo de la segunda revisión.
7. **Guarda los comprobantes** digitales y en papel.

## Centros de revisión técnica

La ficha municipal lista cinco centros: **Los Chillos** (Autopista General Rumiñahui, km 5), **Carapungo** (Panamericana Norte, km 11), **Guajaló** (Av. Maldonado, Panamericana Sur, km 9), **San Isidro** (Los Guayabos 370 y Álamos) y **Guamaní** (calle H y Leónidas Mata, La Perla). Atención según la ficha: lunes a viernes de 08:00 a 17:00 y sábados de 08:00 a 12:00. El Municipio atiende consultas en el 1800 268 268 y en serviciosciudadanos@quito.gob.ec.

## Qué llevar

- Cédula del propietario, o autorización si va otra persona.
- Matrícula original.
- Comprobante de pago de la revisión, del adhesivo y del rodaje.
- Vehículo con luces, llantas, frenos y parabrisas en buen estado.
- Para el Certificado Único Vehicular, el trámite se hace por gob.ec ([CUV](/certificado-unico-vehicular/)).

## Errores frecuentes en Quito

- Dejar el trámite para el último día del mes.
- Ir sin haber cancelado multas pendientes.
- Pensar que la segunda revisión no vence: tiene plazo.
- Confundir el adhesivo de la revisión con la matrícula.
- Pagar a terceros fuera de los canales oficiales.

## Otras gestiones en Quito

[Cambio de propietario](/cambio-de-propietario-vehicular/), [duplicado de matrícula](/duplicado-de-matricula-vehicular/), [duplicado de placas](/duplicado-de-placas-vehiculares/) y [consulta de multas](/consulta-multas-transito/). Si tu vehículo es eléctrico, revisa [eléctricos](/vehiculos-electricos-exoneracion-matricula/).

## Cómo verificar que la información está vigente

Esta página resume datos con la fecha de revisión indicada arriba. Las tarifas y los horarios pueden cambiar por resolución. Antes de pagar, compara con la AMT y con la ficha municipal. Si ves una diferencia, [escríbenos](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-vehicular-guayaquil -->
---
title: "Matriculación vehicular en Guayaquil: guía práctica"
description: "Matricula tu vehículo en Guayaquil: mes según placa, tarifario 2026 de revisión técnica, recargos de USD 50 y 100, tasas y centros. Datos oficiales de la ATM."
h1: "Matriculación vehicular en Guayaquil"
short: "Guayaquil"
type: local
parent: matriculacion-por-ciudad
schema: Article
updated: 2026-10-27
quick: "En Guayaquil el tránsito lo gestiona la Empresa Pública Municipal de Tránsito y Movilidad (ATM). Según su tarifario 2026, la revisión de un liviano particular cuesta USD 29,87; el recargo por atraso es de USD 50 (particulares) o USD 100 (públicos)."
related: [revision-tecnica-vehicular-guayaquil, calendario-matriculacion-vehicular, valor-a-pagar-matricula, multas-por-no-matricular-vehiculo, pago-matricula-linea]
sources:
  - {t: "ATM Guayaquil: tarifario 2026 (Memorando EPMTMG-DFI-2026-0143-M)", u: "https://www.atm.gob.ec"}
  - {t: "Diario Expreso", u: "https://www.expreso.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
verify:
  - "Tarifario 2026 tomado del memorando del 19 de enero de 2026; confirmar que no haya una reforma posterior."
  - "Prórrogas sin multa por dígito (4 hasta el 6 de junio; 1 hasta el 14 de marzo) son avisos puntuales de 2026, no reglas permanentes."
faq:
  - q: "¿Quién gestiona la matrícula en Guayaquil?"
    a: "La Empresa Pública Municipal de Tránsito y Movilidad de Guayaquil EP, conocida como ATM, en coordinación con el SRI y el SPPAT."
  - q: "¿Cuánto cuesta la revisión técnica de un liviano particular?"
    a: "USD 29,87 la primera revisión, la segunda es gratuita, y USD 14,94 la tercera y USD 29,87 la cuarta, según el tarifario 2026."
  - q: "¿Cuánto es el recargo por atraso?"
    a: "USD 50 para vehículos particulares y USD 100 para públicos por retraso en el proceso completo de matriculación dentro del calendario."
  - q: "¿Cuántas oportunidades tengo para aprobar?"
    a: "Hasta cuatro, y la segunda no tiene costo."
  - q: "¿Cómo sé mi mes?"
    a: "Por el último dígito de la placa. Mira el [calendario](/calendario-matriculacion-vehicular/)."
---
## Cómo funciona en Guayaquil

El tránsito de Guayaquil lo gestiona la **Empresa Pública Municipal de Tránsito y Movilidad de Guayaquil EP**, conocida como **ATM** (la prensa también la llama Agencia de Tránsito y Movilidad). Tiene su propio tarifario, sus centros de revisión técnica y su calendario de prórrogas, de modo que los valores de otras ciudades no se pueden dar por buenos aquí.

## Tu mes de matriculación

| Último dígito | Mes |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

Diciembre es para rezagados. En 2026 la ATM amplió plazos sin multa en algunos casos: la placa terminada en 4 hasta el 6 de junio y la terminada en 1 hasta el 14 de marzo. Son extensiones puntuales; no cuentes con ellas. Los casos de mora están en el [calendario](/calendario-matriculacion-vehicular/).

## Tarifario 2026 de revisión técnica

Según el memorando EPMTMG-DFI-2026-0143-M del 19 de enero de 2026, en dólares. La **segunda revisión no tiene costo**.

| Clase | Primera | Tercera | Cuarta |
|---|---|---|---|
| Moto | 18,03 | 9,02 | 18,03 |
| Liviano particular | 29,87 | 14,94 | 29,87 |
| Alquiler, escolar y taxi | 20,79 | 10,39 | 20,79 |
| Buses y camiones medianos | 40,79 | 20,41 | 40,79 |
| Camiones pesados | 48,64 | 24,33 | 48,64 |

La RTV Móvil agrega USD 12,66. Más detalle en [revisión técnica en Guayaquil](/revision-tecnica-vehicular-guayaquil/).

## Otras tasas de la ATM (2026)

| Trámite | Tasa (USD) |
|---|---|
| Adhesivo de revisión | 3,90 |
| Duplicado del adhesivo | 5,62 |
| Certificado de vehículo exento de revisión | 13,35 |
| Historial y certificados | 8,07 |
| Cambio de características | 13,23 |
| Transferencia de dominio | 13,23 |
| Cambio de servicio | 74,81 |
| Bloqueo o desbloqueo | 11,52 |
| Baja | 11,52 |
| Certificado Único Vehicular | 8,63 |
| Duplicado de matrícula de vehículo | 37,59 |
| Duplicado de matrícula de moto | 23,27 |
| Verificación de chasis y motor | 27,63 |
| Documento habilitante de matriculación | 22,00 |

## Recargos

- **USD 50** para vehículos particulares y **USD 100** para públicos, por retraso en el proceso completo de matriculación dentro del calendario.
- **5 % del SBU** si el vehículo aprobó pero no tiene adhesivo.
- No registrar el traspaso en 30 días es infracción del artículo 392, numeral 13, del COIP.

## Paso a paso en Guayaquil

1. **Consulta deudas y multas** con la placa en la ATM, el SRI y la ANT.
2. **Ve a un centro de revisión.** En 2026 los turnos en línea están suspendidos desde el 2 de marzo, según Expreso; se atiende directamente.
3. **Paga la revisión** según tu clase de vehículo.
4. **Si aprobaste,** paga los rubros de matrícula: impuesto, SPPAT y tasas ([valor a pagar](/valor-a-pagar-matricula/)).
5. **Obtén la matrícula** y el adhesivo, y verifica los datos.
6. **Guarda los comprobantes.**

## Centros y horarios

Según Expreso (30 de mayo de 2026), los centros están en el norte, el sur y la vía a Daule, operados por el consorcio SGS. Atienden de lunes a viernes de 07:00 a 18:00 y sábados de 07:00 a 13:00. Verifica la dirección exacta en la ATM antes de ir.

## Qué documentos llevar

- Cédula del propietario o autorización firmada.
- Placa y matrícula anterior.
- Comprobantes de pago cuando el centro los pida.
- Vehículo con luces, llantas, frenos y parabrisas en buen estado.

## Multas y bloqueos

Debes tener las multas canceladas antes de pagar. Si el vehículo está bloqueado, el proceso está en [desbloqueo vehicular](/bloqueo-vehicular-desbloqueo/). Si estás atrasado, mira [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Errores comunes

- Esperar a diciembre, cuando se saturan los centros.
- Confundir el adhesivo con la matrícula.
- Agendar turno en línea cuando está suspendido.
- Usar intermediarios sin comprobante.

## Trámites relacionados

[Cambio de propietario](/cambio-de-propietario-vehicular/), [duplicado de matrícula](/duplicado-de-matricula-vehicular/), [placas](/duplicado-de-placas-vehiculares/), [CUV](/certificado-unico-vehicular/) y [matrícula de motos](/matricula-moto/).

## Cómo mantener la información al día

La ATM actualiza su tarifario por memorando y puede cambiar canales durante el año. Para cualquier pago, el portal oficial prevalece. Si detectas una diferencia, [avísanos](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-vehicular-cuenca -->
---
title: "Matriculación vehicular en Cuenca: guía práctica"
description: "Cómo matricular tu vehículo en Cuenca con la EMOV EP: centros Mayancela y Capulispamba, requisitos 2026, adhesivo de USD 5, costos de trámites y mes por placa."
h1: "Matriculación vehicular en Cuenca"
short: "Cuenca"
type: local
parent: matriculacion-por-ciudad
schema: Article
updated: 2026-10-27
quick: "En Cuenca la EMOV EP gestiona la matrícula. La revisión se hace en Mayancela o Capulispamba con turno en línea, el adhesivo cuesta USD 5 y debes pagar la matrícula, la tasa de movilidad y el rodaje antes de pedir el turno."
related: [revision-tecnica-vehicular-cuenca, calendario-matriculacion-vehicular, valor-a-pagar-matricula, multas-por-no-matricular-vehiculo, turno-matriculacion-vehicular]
sources:
  - {t: "EMOV EP Cuenca: requisitos de matriculación 2026", u: "https://www.emov.gob.ec"}
  - {t: "EMOV EP: guía de trámites", u: "https://www.emov.gob.ec"}
  - {t: "ANT: tarifario 2026", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Tarifa de la revisión técnica en Cuenca: no se encontró el valor vigente en la fuente oficial. Confirmar con EMOV EP antes de publicar una cifra."
  - "Costo del CUV en Cuenca (USD 10) proviene del documento de requisitos de la EMOV; el tarifario nacional de la ANT también indica USD 10."
faq:
  - q: "¿Quién gestiona la matrícula en Cuenca?"
    a: "La Empresa Pública de Movilidad, Tránsito y Transporte, EMOV EP, que también administra los centros de revisión técnica."
  - q: "¿Dónde se hace la revisión técnica?"
    a: "En Mayancela (vehículos pesados, particulares, públicos y comerciales) o en Capulispamba (livianos particulares y motos), con turno en línea en emov.gob.ec."
  - q: "¿Cuánto cuesta el adhesivo?"
    a: "USD 5, según la EMOV."
  - q: "¿Qué debo pagar antes de pedir el turno?"
    a: "La matrícula anual, la tasa de revisión, el rodaje y el certificado de no adeudar a la EMOV, además de las multas."
  - q: "¿Cuánto dura el documento de matrícula?"
    a: "Al renovar se entrega un documento con vigencia de cinco años, según la resolución 018-DIR-2022-ANT citada por la EMOV."
---
## Cómo funciona en Cuenca

En Cuenca la **EMOV EP** gestiona la movilidad, la matriculación y la revisión técnica. Hay dos centros de revisión y puntos de matriculación en la Terminal Terrestre y en el Parque de la Madre. La EMOV asegura que su revisión es la más barata del país, aunque no pudimos contrastar la cifra vigente en su portal.

## Tu mes de matriculación

| Último dígito | Mes |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

En el calendario de la EMOV, septiembre corresponde al dígito 8. Diciembre es obligatorio para la revisión de todas las placas rezagadas, y los taxis tienen su propio periodo en enero. Más en el [calendario nacional](/calendario-matriculacion-vehicular/).

## Centros de revisión técnica

- **Mayancela:** vehículos pesados, particulares, públicos y comerciales. Teléfono (07) 289935.
- **Capulispamba:** livianos particulares y motos, en la Panamericana Norte. Teléfono (07) 2876059.

Atención en ambos: lunes a viernes de 08:00 a 17:00 y sábados de 08:00 a 12:00. Las oficinas principales de la EMOV (Carlos Arízaga y Tarquino Cordero) atienden de 08:00 a 13:00 y de 15:00 a 18:00; su teléfono es (07) 2855481.

## Requisitos 2026 para renovar

1. **Aprobar la revisión técnica** con turno en línea en emov.gob.ec.
2. **Pagar la tasa de movilidad ecológica y sostenible.**
3. **Obtener el certificado de no adeudar** a la EMOV.
4. **Pagar la matrícula anual y las multas** en una entidad financiera con 48 horas de anticipación.
5. **Pagar el rodaje** (Cooperativa JEP, Banco del Pacífico o puntos de la EMOV).
6. **Cancelar multas de la ANT y de fotocontrol.**
7. **Tener un correo electrónico** registrado.

Antes de agendar el turno en línea debes haber pagado matrícula, tasa de revisión, rodaje y certificado. El adhesivo cuesta **USD 5**.

## Costos de trámites en Cuenca

Valores del documento de requisitos de la EMOV (2026), en dólares:

| Trámite | Costo |
|---|---|
| Certificado Único Vehicular | 10,00 |
| Especie de matrícula (duplicado) | 22,00 |
| Traspaso de dominio | 7,00 |
| Cambio de color, clase o tipo | 8,00 |
| Placas nuevas (vehículo) | 34,00 |
| Placas nuevas (moto) | 17,00 |
| Duplicado de placas | 26,00 o 15,00 según la categoría |

Las placas se pagan con orden de la ANT en el Banco del Pacífico. Más detalle en [duplicado de placas](/duplicado-de-placas-vehiculares/) y [duplicado de matrícula](/duplicado-de-matricula-vehicular/).

## Paso a paso en Cuenca

1. Consulta multas en la EMOV y en la ANT.
2. Paga matrícula, tasa, rodaje y certificado.
3. Agenda el turno en línea en el centro que te corresponda.
4. Pasa la revisión.
5. Con la revisión aprobada, acude al punto de matriculación y recibe el documento.

## Errores frecuentes

- Pedir el turno sin haber pagado antes.
- Pagar la matrícula el mismo día del trámite en lugar de 48 horas antes.
- Ir al centro equivocado: las motos y livianos van a Capulispamba.
- Dejar todo para diciembre.

## Trámites relacionados

[Cambio de propietario](/cambio-de-propietario-vehicular/), [CUV](/certificado-unico-vehicular/), [revisión técnica en Cuenca](/revision-tecnica-vehicular-cuenca/) y [multas](/multas-por-no-matricular-vehiculo/).

## Cómo mantener la información al día

La EMOV publica sus requisitos por año. Comprueba la versión vigente en su portal antes de pagar; si ves una diferencia, [escríbenos](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-vehicular-ambato -->
---
title: "Matriculación vehicular en Ambato: cómo hacerlo"
description: "Matricula tu vehículo en Ambato (Tungurahua): mes según placa, qué entidad atiende (municipio o Mancomunidad), pagos, revisión técnica y atención 2026."
h1: "Matriculación vehicular en Ambato"
short: "Ambato"
type: local
parent: matriculacion-por-ciudad
schema: Article
updated: 2026-10-27
quick: "En Ambato el mes lo define el último dígito de la placa. La provincia cuenta con la Mancomunidad de Tránsito de Tungurahua (Pelileo), y el municipio mantiene su centro de revisión en Shuyurco. Confirma con cuál debes tramitar tu vehículo."
related: [calendario-matriculacion-vehicular, valor-a-pagar-matricula, revision-tecnica-vehicular, multas-por-no-matricular-vehiculo, matriculacion-por-ciudad]
sources:
  - {t: "Mancomunidad de Tránsito de Tungurahua", u: "https://www.transitotungurahua.gob.ec"}
  - {t: "La Hora: reactivación del servicio, marzo 2026", u: "https://www.lahora.com.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Entidad que atiende hoy a los vehículos de Ambato (GAD municipal o Mancomunidad): confirmar antes de publicar como regla."
  - "Tarifa de revisión técnica en Ambato: una publicación de 2026 muestra valores iguales a los de Quito; no se encontró fuente oficial. No publicada."
  - "Teléfono (03) 2997800 ext. 3332 y exoneración de modelos 2021 o posteriores provienen de un aviso de 2023; pueden estar desactualizados."
faq:
  - q: "¿Cuál es mi mes en Ambato?"
    a: "El mismo que en todo el país, según el último dígito de la placa: [calendario](/calendario-matriculacion-vehicular/)."
  - q: "¿Quién atiende los trámites?"
    a: "Tungurahua cuenta con la Mancomunidad de Tránsito, con sede en Pelileo, que agrupa ocho cantones. El municipio de Ambato mantiene un centro de revisión técnica en la calle 6, sector Shuyurco. Confirma cuál corresponde a tu trámite."
  - q: "¿Dónde pago?"
    a: "La matrícula y el tributo provincial en bancos o cooperativas autorizadas; el rodaje, la revisión y el adhesivo en las ventanillas de la entidad. Mira [pago en línea](/pago-matricula-linea/)."
  - q: "¿Qué hago si me atrasé?"
    a: "Consulta recargos, cancela multas y matricula. Detalles en [multas por no matricular](/multas-por-no-matricular-vehiculo/)."
---
## Qué debes saber para matricular en Ambato

Los vehículos de Ambato siguen las reglas nacionales: **el mes depende del último dígito de la placa** y el total se compone de impuestos, SPPAT y tasas. Lo que cambia entre ciudades es quién gestiona el trámite, dónde se revisa el vehículo y cómo se agenda.

## Quién atiende en Tungurahua

Tungurahua cuenta ahora con la **Mancomunidad de Tránsito de Tungurahua**, una empresa pública que agrupa ocho cantones y tiene su sede en Pelileo (calles Inmortal y Curarary). Ofrece matriculación, traspaso, duplicados, vehículos nuevos, cambio de servicio y de características, bloqueos, CUV y revisión técnica. Su atención es de lunes a viernes: matriculación de 08:00 a 16:00 y revisión técnica de 07:30 a 16:00.

Por separado, el **Municipio de Ambato** mantiene un centro de revisión técnica en la calle 6, sector Shuyurco, con atención de lunes a viernes de 08:00 a 17:00. Como la distribución de funciones ha cambiado en los últimos años, confirma en la entidad correspondiente cuál atiende tu caso.

## Tu mes de matriculación

| Último dígito | Mes |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

Diciembre es para rezagados. En marzo de 2026, La Hora informó que el servicio se restableció el 9 de marzo tras el incidente del sistema de la ANT, que la placa 1 quedó sin multa de calendarización hasta el 31 de diciembre y que los turnos se atendían de forma presencial.

## Dónde se paga

Según la Mancomunidad:

- **Ventanilla de la entidad:** revisión técnica, rodaje (excepto en Ambato y Pelileo), certificados, bloqueos y duplicados.
- **Banco del Pacífico y Cooperativa El Sagrario:** matrícula y tributo del Consejo Provincial.

Un aviso municipal de 2023, que puede haber cambiado, pedía pagar matrícula y tributo provincial en bancos 48 horas antes, y rodaje, revisión y adhesivo en las ventanillas municipales.

## Paso a paso en Ambato

1. **Consulta multas y deudas** con la placa.
2. **Confirma la entidad** que atiende tu trámite.
3. **Paga matrícula y tributo provincial** con anticipación.
4. **Pasa la revisión técnica** en el centro correspondiente.
5. **Paga rodaje y adhesivo** en la ventanilla.
6. **Retira tu matrícula** y verifica los datos.

## Revisión técnica

Para el marco general, mira [revisión técnica vehicular](/revision-tecnica-vehicular/). La tarifa local no se publica aquí hasta contar con una fuente oficial.

## Errores frecuentes

- Presentarse en la entidad que no corresponde.
- Pagar el mismo día en lugar de anticipar.
- Confiar en avisos antiguos sobre exoneraciones por año modelo.
- Dejar el trámite para diciembre.

## Mantén la información al día

Esta guía se actualizará cuando la entidad publique tarifas oficiales. Si tienes datos recientes, [escríbenos](/contacto/). Para el resto de ciudades, mira [matrícula por ciudad](/matriculacion-por-ciudad/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-vehicular-riobamba -->
---
title: "Matriculación vehicular en Riobamba: guía práctica"
description: "Matricula tu vehículo en Riobamba: gestión municipal, mes según placa, centro de revisión técnica, horarios de atención, turnos en línea y requisitos."
h1: "Matriculación vehicular en Riobamba"
short: "Riobamba"
type: local
parent: matriculacion-por-ciudad
schema: Article
updated: 2026-10-27
quick: "En Riobamba el trámite lo gestiona el GAD Municipal (Dirección de Movilidad). La revisión técnica se hace en el CRTV de Mérida y Caracas, y los turnos se piden en la plataforma Movilidad Riobamba. El mes lo define el último dígito de la placa."
related: [calendario-matriculacion-vehicular, valor-a-pagar-matricula, revision-tecnica-vehicular, multas-por-no-matricular-vehiculo, matriculacion-por-ciudad]
sources:
  - {t: "GAD Municipal de Riobamba: Dirección de Movilidad", u: "https://www.gadmriobamba.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Tarifa de revisión técnica en Riobamba: no se encontró fuente oficial. No publicada."
  - "Los requisitos se publican como imágenes en el portal municipal; confirmar cada trámite directamente."
faq:
  - q: "¿Quién gestiona la matrícula en Riobamba?"
    a: "El GAD Municipal de Riobamba, a través de su Dirección de Movilidad."
  - q: "¿Dónde se hace la revisión técnica?"
    a: "En el Centro de Revisión Técnica Vehicular, en las calles Mérida y Caracas, detrás del Mercado Mayorista."
  - q: "¿Cómo pido turno?"
    a: "En la Plataforma Movilidad Riobamba del portal del municipio."
  - q: "¿Cuál es mi mes?"
    a: "El que marca el último dígito de tu placa. Mira el [calendario](/calendario-matriculacion-vehicular/)."
---
## Cómo funciona en Riobamba

El **GAD Municipal de Riobamba** gestiona la matriculación por medio de su Dirección de Movilidad. El sistema opera sobre la plataforma AXIS, la misma que sufrió la interrupción de principios de 2026; el 9 de marzo de ese año se reactivó el servicio en 127 municipios autorizados.

## Dónde y cuándo

- **Oficinas de la Dirección de Movilidad:** 5 de Junio y Primera Constituyente, lunes a viernes de 08:00 a 18:00.
- **Centro de Revisión Técnica Vehicular (CRTV):** calles Mérida y Caracas, detrás del Mercado Mayorista.
- **Turnos:** Plataforma Movilidad Riobamba, en el portal del municipio.

## Tu mes de matriculación

| Último dígito | Mes |
|---|---|
| 1 | Febrero |
| 2 | Marzo |
| 3 | Abril |
| 4 | Mayo |
| 5 | Junio |
| 6 | Julio |
| 7 | Agosto |
| 8 | Septiembre |
| 9 | Octubre |
| 0 | Noviembre |

Diciembre es para rezagados. Más en el [calendario nacional](/calendario-matriculacion-vehicular/).

## Trámites que ofrece la Dirección de Movilidad

El municipio publica requisitos para renovación de matrícula (particular y pública), traspaso, duplicados de matrícula y de placas, cambio de motor y cambio de servicio, entre otros. Los requisitos están en imágenes en su portal, por lo que conviene revisarlos directamente antes de acudir.

## Paso a paso

1. **Consulta multas y deudas** con la placa.
2. **Pide turno** en la plataforma municipal.
3. **Pasa la revisión técnica** en el CRTV.
4. **Paga los rubros** de matrícula ([valor a pagar](/valor-a-pagar-matricula/)).
5. **Retira tu matrícula.**

## Qué llevar

- Cédula del propietario, o autorización si va otra persona.
- Matrícula anterior y comprobantes de pago de impuestos cuando se pidan.
- El vehículo con luces, llantas y frenos en buen estado para la revisión.

## Reactivación del servicio en 2026

Tras la interrupción del sistema de la ANT a inicios de 2026, el 9 de marzo se autorizó la reactivación en 127 municipios, entre ellos los que usan AXIS. Si tu trámite se vio afectado, pregunta en la Dirección de Movilidad si tu placa tiene una extensión sin multa.

## Errores frecuentes

- Ir sin turno.
- No cancelar multas antes de iniciar.
- Dejarlo para diciembre.

## Mantén la información al día

La tarifa local de revisión no se publica en esta guía por falta de una fuente oficial. Si la tienes, [escríbenos](/contacto/). Más en [revisión técnica vehicular](/revision-tecnica-vehicular/) y [multas](/multas-por-no-matricular-vehiculo/).
<!-- PAGE:END -->

<!-- PAGE:START slug=revision-tecnica-vehicular-quito -->
---
title: "Revisión técnica vehicular en Quito: costos 2026"
description: "Tarifas 2026 de la revisión técnica en Quito por tipo de vehículo, adhesivo de USD 5, plazos de la segunda y tercera revisión, centros y multas."
h1: "Revisión técnica vehicular en Quito"
short: "RTV Quito"
type: local
parent: revision-tecnica-vehicular
schema: Article
updated: 2026-10-27
quick: "En Quito la revisión de un liviano cuesta USD 31,56 (primera) y USD 15,80 (tercera), más USD 5 de adhesivo. Tienes 45 días para la segunda revisión y 30 para la tercera y la cuarta."
related: [matriculacion-vehicular-quito, revision-tecnica-vehicular, valor-a-pagar-matricula, turno-matriculacion-vehicular, multas-por-no-matricular-vehiculo]
sources:
  - {t: "Municipio de Quito: ficha RTV (GADDMQ-MO-AMT-39)", u: "https://pam.quito.gob.ec"}
  - {t: "Primicias", u: "https://www.primicias.ec"}
  - {t: "Quito Informa", u: "https://www.quitoinforma.gob.ec"}
verify:
  - "Tarifas tomadas de Primicias (fuente AMT, enero 2026). La ficha municipal indica el valor como variable sin cifras; contrastar con el portal de la AMT."
faq:
  - q: "¿Cuánto cuesta la revisión técnica en Quito?"
    a: "En 2026: livianos USD 31,56, motos USD 18,55, taxis USD 21,40, buses USD 42, busetas USD 21,30 y pesados USD 50, para la primera revisión."
  - q: "¿Cuánto cuesta la tercera revisión?"
    a: "La mitad aproximadamente: USD 15,80 en livianos, USD 9,30 en motos y USD 10,70 en taxis."
  - q: "¿Cuánto tiempo tengo para la segunda revisión?"
    a: "Hasta 45 días; la tercera y la cuarta, 30 días, dentro del periodo de convocatoria."
  - q: "¿Qué pasa si no apruebo ni acudo?"
    a: "La multa por convocatoria es de USD 50, según la AMT."
---
## Cómo funciona en Quito

La revisión técnica vehicular es un requisito para matricular. En Quito la realizan los centros municipales y, si el vehículo aprueba, se matricula en el mismo centro. Esta guía se concentra en costos, plazos y preparación; para el proceso completo mira [matriculación en Quito](/matriculacion-vehicular-quito/).

## Tarifas 2026

Valores en dólares, publicados en enero de 2026 con datos de la AMT. La primera columna es la primera revisión; la segunda, la tercera revisión.

| Clase | Primera | Tercera |
|---|---|---|
| Buses | 42,00 | 21,00 |
| Busetas | 21,30 | 10,70 |
| Livianos | 31,56 | 15,80 |
| Motos | 18,55 | 9,30 |
| Pesados | 50,00 | 25,00 |
| Plataformas | 18,55 | 9,30 |
| Taxis | 21,40 | 10,70 |
| Exonerados | 8,80 | |

Aparte se paga el **adhesivo (USD 5,00)** y el impuesto al rodaje.

## Plazos si no apruebas

La ficha municipal establece: segunda revisión dentro de 45 días; tercera, dentro de 30; cuarta, dentro de 30. Solo valen dentro del periodo de la convocatoria anual. La multa por no acudir o no aprobar en la convocatoria es de USD 50.

## Centros

Los Chillos, Carapungo, Guajaló, San Isidro y Guamaní. Direcciones en [matriculación en Quito](/matriculacion-vehicular-quito/). Horario según la ficha municipal: lunes a viernes de 08:00 a 17:00 y sábados de 08:00 a 12:00.

## Requisitos

- Cédula y matrícula original.
- No tener deudas con la AMT, el SRI ni la ANT.
- Pago de la revisión, del adhesivo y del rodaje.

## Cómo prepararte

- Revisa luces, direccionales y frenos.
- Verifica llantas, parabrisas y limpiaparabrisas.
- Lleva el vehículo limpio y con el motor en buen estado.
- No dejes la revisión para el último día de tu mes ([calendario](/calendario-matriculacion-vehicular/)).

## Errores frecuentes

- Perder el plazo de la segunda revisión.
- Asumir que el valor es el mismo para todas las clases.
- No considerar el adhesivo y el rodaje.

## Más información

[Turnos](/turno-matriculacion-vehicular/), [multas](/multas-por-no-matricular-vehiculo/) y [valor a pagar](/valor-a-pagar-matricula/).
<!-- PAGE:END -->

<!-- PAGE:START slug=revision-tecnica-vehicular-guayaquil -->
---
title: "Revisión técnica vehicular en Guayaquil: costos 2026"
description: "Tarifas 2026 de la revisión técnica en Guayaquil por clase de vehículo, segunda revisión gratis, hasta cuatro oportunidades, centros y horarios de la ATM."
h1: "Revisión técnica vehicular en Guayaquil"
short: "RTV Guayaquil"
type: local
parent: revision-tecnica-vehicular
schema: Article
updated: 2026-10-27
quick: "En Guayaquil un liviano particular paga USD 29,87 la primera revisión; la segunda es gratis, la tercera cuesta USD 14,94 y la cuarta USD 29,87. Tienes hasta cuatro oportunidades."
related: [matriculacion-vehicular-guayaquil, revision-tecnica-vehicular, valor-a-pagar-matricula, turno-matriculacion-vehicular, multas-por-no-matricular-vehiculo]
sources:
  - {t: "ATM Guayaquil: tarifario 2026", u: "https://www.atm.gob.ec"}
  - {t: "Diario Expreso", u: "https://www.expreso.ec"}
verify:
  - "Tarifario del memorando EPMTMG-DFI-2026-0143-M (19 ene 2026); confirmar vigencia."
faq:
  - q: "¿Cuánto cuesta la revisión de un auto particular en Guayaquil?"
    a: "USD 29,87 la primera, gratis la segunda, USD 14,94 la tercera y USD 29,87 la cuarta."
  - q: "¿Cuánto cuesta para una moto?"
    a: "USD 18,03 la primera, USD 9,02 la tercera y USD 18,03 la cuarta."
  - q: "¿Cuántas veces puedo intentar?"
    a: "Hasta cuatro, y la segunda es gratuita."
  - q: "¿Puedo sacar turno en línea?"
    a: "Desde el 2 de marzo de 2026 los turnos en línea estaban suspendidos y se atendía directamente en los centros, según Expreso."
---
## Cómo funciona en Guayaquil

La revisión técnica es requisito para matricular. En Guayaquil la gestiona la ATM con centros operados por un consorcio, y sus tarifas se fijan por memorando propio, distintas a las de otras ciudades. Mira el proceso completo en [matriculación en Guayaquil](/matriculacion-vehicular-guayaquil/).

## Tarifario 2026

Valores en dólares, según el memorando del 19 de enero de 2026:

| Clase | Primera | Segunda | Tercera | Cuarta |
|---|---|---|---|---|
| Moto | 18,03 | Gratis | 9,02 | 18,03 |
| Liviano particular | 29,87 | Gratis | 14,94 | 29,87 |
| Alquiler, escolar y taxi | 20,79 | Gratis | 10,39 | 20,79 |
| Buses y camiones medianos | 40,79 | Gratis | 20,41 | 40,79 |
| Camiones pesados | 48,64 | Gratis | 24,33 | 48,64 |

La **RTV Móvil** agrega USD 12,66. El adhesivo cuesta USD 3,90 y su duplicado, USD 5,62.

## Vehículos exentos

El certificado de vehículo exento de revisión tiene una tasa de USD 13,35.

## Centros y horarios

Según Expreso, los centros están en el norte, el sur y la vía a Daule, con atención de lunes a viernes de 07:00 a 18:00 y sábados de 07:00 a 13:00.

## Si no apruebas

Tienes hasta cuatro oportunidades. Corrige las observaciones antes de regresar; la segunda revisión no tiene costo. Un vehículo aprobado sin adhesivo se expone a una sanción equivalente al 5 % del SBU, así que verifica que te lo coloquen al terminar. Si te atrasas respecto de tu mes, el recargo es de USD 50 para particulares y USD 100 para públicos.

## Cómo prepararte

- Luces, direccionales y frenos en buen estado.
- Llantas con labrado suficiente.
- Parabrisas sin fisuras que afecten la visión.
- Documentos: cédula y matrícula.

## Errores frecuentes

- Dejar la revisión para diciembre.
- Intentar sacar turno en línea cuando está suspendido.
- No corregir las observaciones antes de la segunda revisión.

## Más información

[Turnos](/turno-matriculacion-vehicular/), [multas](/multas-por-no-matricular-vehiculo/) y [valor a pagar](/valor-a-pagar-matricula/).
<!-- PAGE:END -->

<!-- PAGE:START slug=revision-tecnica-vehicular-cuenca -->
---
title: "Revisión técnica vehicular en Cuenca: centros y pasos"
description: "Revisión técnica en Cuenca con la EMOV EP: centros Mayancela y Capulispamba, horarios, turno en línea, adhesivo de USD 5 y qué pagar antes."
h1: "Revisión técnica vehicular en Cuenca"
short: "RTV Cuenca"
type: local
parent: revision-tecnica-vehicular
schema: Article
updated: 2026-10-27
quick: "En Cuenca la revisión la hace la EMOV EP en Mayancela o Capulispamba, con turno en línea. El adhesivo cuesta USD 5. Antes del turno debes pagar la matrícula, la tasa de revisión, el rodaje y el certificado de no adeudar."
related: [matriculacion-vehicular-cuenca, revision-tecnica-vehicular, valor-a-pagar-matricula, turno-matriculacion-vehicular, multas-por-no-matricular-vehiculo]
sources:
  - {t: "EMOV EP Cuenca", u: "https://www.emov.gob.ec"}
  - {t: "ANT: tarifario 2026", u: "https://www.ant.gob.ec"}
verify:
  - "Tarifa de la revisión en Cuenca: no se encontró cifra oficial vigente. Confirmar con EMOV EP. No se publica el valor de USD 20 usado antes."
faq:
  - q: "¿Cuánto cuesta la revisión técnica en Cuenca?"
    a: "El valor lo fija la EMOV EP y no lo hemos podido confirmar en su portal. El adhesivo cuesta USD 5. Consulta la tasa vigente antes de pagar."
  - q: "¿A qué centro debo ir?"
    a: "Los livianos particulares y las motos, a Capulispamba; los vehículos pesados, públicos y comerciales, a Mayancela."
  - q: "¿Necesito turno?"
    a: "Sí, en línea en emov.gob.ec, después de pagar los rubros previos. Mira [turnos](/turno-matriculacion-vehicular/)."
  - q: "¿Qué hago si no apruebo?"
    a: "Corriges las observaciones y regresas dentro del plazo que fije la Ordenanza; en casos de fuerza mayor la EMOV permite solicitar una extensión del plazo."
---
## Cómo funciona en Cuenca

La **EMOV EP** gestiona la revisión técnica de Cuenca. Es un requisito previo a la matrícula y se hace en dos centros. La EMOV afirma que su revisión es la más económica del país; como no pudimos confirmar la tarifa vigente, no publicamos una cifra.

## Centros y horarios

- **Mayancela:** vehículos pesados, particulares, públicos y comerciales. Teléfono (07) 289935.
- **Capulispamba:** livianos particulares y motos, Panamericana Norte. Teléfono (07) 2876059.

Atención: lunes a viernes de 08:00 a 17:00 y sábados de 08:00 a 12:00.

## Qué pagar antes del turno

1. Matrícula anual y multas, en una entidad financiera, con 48 horas de anticipación.
2. Tasa de revisión.
3. Rodaje.
4. Certificado de no adeudar a la EMOV.
5. Tasa de movilidad ecológica y sostenible.

Luego pide el turno en línea. El **adhesivo cuesta USD 5**.

## Si no apruebas

Corrige las observaciones y regresa a la segunda revisión dentro del plazo. Si por fuerza mayor no puedes acudir a la segunda, tercera o cuarta revisión en estado condicional, puedes pedir una extensión del plazo con justificaciones, según la Ordenanza citada por la EMOV (Registro Oficial 413 de 2006).

## Cómo prepararte

- Revisa luces, frenos y llantas.
- Lleva cédula y matrícula.
- Ten tu comprobante de pago a mano.
- Si tu vehículo es una moto o un liviano particular, ve a Capulispamba; si es pesado, público o comercial, a Mayancela.
- Llega con tiempo: los sábados el horario termina a las 12:00.

## Costos relacionados

Para tu referencia, el documento de requisitos de la EMOV (2026) indica USD 10,00 para el Certificado Único Vehicular, USD 22,00 por la especie de matrícula y USD 7,00 por el traspaso de dominio. Estos valores no sustituyen la tarifa de la revisión, que debes consultar en la EMOV.

## Errores frecuentes

- Pedir el turno sin pagar antes los rubros.
- Ir al centro equivocado.
- Dejar la revisión para diciembre.

## Más información

[Matriculación en Cuenca](/matriculacion-vehicular-cuenca/), [turnos](/turno-matriculacion-vehicular/), [multas](/multas-por-no-matricular-vehiculo/) y [valor a pagar](/valor-a-pagar-matricula/).
<!-- PAGE:END -->

<!-- PAGE:START slug=certificado-unico-vehicular -->
---
title: "Certificado Único Vehicular (CUV): qué es y cómo pedirlo"
description: "Qué es el Certificado Único Vehicular en Ecuador, qué información muestra, para qué sirve al comprar o vender y cómo obtenerlo."
h1: "Certificado Único Vehicular (CUV) en Ecuador"
short: "CUV"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "El CUV es el documento oficial que reúne los datos del vehículo, su propietario, gravámenes, bloqueos y estado. Se pide en el canal de la ANT o de tu municipio, con un costo de referencia de USD 7,50 a 10, y es clave antes de comprar o vender."
related: [cambio-de-propietario-vehicular, bloqueo-vehicular-desbloqueo, consulta-multas-transito, multas-por-no-matricular-vehiculo, tramites-vehiculares]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Costo del CUV (referencia USD 7,50 a 10) y canal de emisión actual: confirmar."
faq:
  - q: "¿Cuánto cuesta el CUV?"
    a: "Como referencia, entre USD 7,50 y 10. Confirma el valor actual en el canal oficial."
  - q: "¿Quién puede solicitarlo?"
    a: "Normalmente el propietario o quien tenga autorización; algunos canales permiten consultar con la placa."
  - q: "¿Cuánto dura vigente?"
    a: "Refleja el estado al momento de emisión. Úsalo cerca de la fecha de la compra y vuelve a consultar antes de firmar."
  - q: "¿Reemplaza a la consulta de multas?"
    a: "No. Complementa la información; las multas se consultan por separado: [consulta de multas](/consulta-multas-transito/)."
---
## Qué es

El **Certificado Único Vehicular (CUV)** es un documento que consolida la información oficial de un vehículo: datos técnicos, propietario registrado, estado de matrícula, gravámenes y bloqueos. Es el equivalente a una «hoja de vida» del vehículo y reduce el riesgo de fraude en compraventas.

## Qué información suele mostrar

| Sección | Contenido típico |
|---|---|
| Identificación | Placa, chasis, motor, marca, modelo, año, color |
| Propietario | Nombre y documento del dueño registrado |
| Estado | Matrícula, servicio, clase |
| Restricciones | Prohibición de enajenar, bloqueos, prenda |
| Historial | Cambios de características o de propietario, según el sistema |

## Para qué sirve

- **Comprar con seguridad:** confirma que quien vende es el dueño y que no hay gravámenes.
- **Vender con respaldo:** demuestra que el vehículo está libre.
- **Trámites:** muchas gestiones (traspaso, baja, cambio de características) lo usan como respaldo.
- **Seguros y créditos:** algunas entidades lo piden.

## Cómo obtenerlo

1. Ingresa al canal oficial de la ANT o de tu municipio.
2. Busca el servicio de certificado vehicular.
3. Ingresa la placa y los datos solicitados.
4. Paga la tasa.
5. Descarga el documento o retíralo según el canal.

Si vas a comprar, pídele al vendedor que lo emita, o emítelo tú con la placa si el sistema lo permite.

## Cómo leerlo antes de comprar

1. **Verifica que el nombre del propietario** coincida con quien vende.
2. **Compara chasis y motor** con el vehículo físico.
3. **Busca restricciones:** prenda, prohibición de enajenar, bloqueos.
4. **Revisa el estado de la matrícula.**
5. **Consulta multas por separado** ([consulta de multas](/consulta-multas-transito/)).

Si aparece algún bloqueo, mira [desbloqueo vehicular](/bloqueo-vehicular-desbloqueo/) antes de pagar.

## Errores comunes

- Confiar en un documento impreso por el vendedor sin verificar.
- Firmar el contrato sin haber revisado el CUV reciente.
- Olvidar que las deudas pueden aparecer después de la emisión.

## Relación con el traspaso

El CUV es el primer paso razonable antes de un [cambio de propietario](/cambio-de-propietario-vehicular/). Después del traspaso, pide uno nuevo con tu nombre para confirmar que el registro quedó actualizado.

## Recomendaciones

Guarda una copia en digital, y no la compartas con desconocidos porque contiene datos personales. Si algo no te cuadra, no compres: el costo del certificado es mínimo frente al riesgo de heredar problemas. Si ya tienes el vehículo y quieres entender el calendario, mira [matriculación anual](/matriculacion-anual-vehicular/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matricula-moto -->
---
title: "Matrícula de moto en Ecuador: pasos, requisitos y costos"
description: "Cómo matricular una motocicleta en Ecuador: calendario por dígito, revisión técnica, SPPAT, valores de referencia y errores comunes."
h1: "Matrícula de moto en Ecuador"
short: "Matrícula de moto"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Las motos se matriculan cada año según el último dígito de la placa. Pagan impuesto, SPPAT y tasas con valores propios y, donde existe, revisión técnica con tarifa para motocicletas."
related: [calendario-matriculacion-vehicular, valor-a-pagar-matricula, revision-tecnica-vehicular-guayaquil, sppat, multas-por-no-matricular-vehiculo]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
verify:
  - "Valores de SPPAT y tasas para motocicletas: confirmar tarifas vigentes."
faq:
  - q: "¿Las motos pagan lo mismo que los autos?"
    a: "No. Los valores dependen del avalúo, cilindraje y clase, y suelen ser menores. Confirma con la consulta del SRI y el estado de cuenta."
  - q: "¿Necesitan revisión técnica?"
    a: "En las ciudades que la exigen, sí, con tarifa para motocicletas. En Guayaquil se cita una referencia cercana a USD 18."
  - q: "¿Es obligatorio el SPPAT?"
    a: "Sí, igual que para cualquier vehículo."
  - q: "¿Cuál es mi mes?"
    a: "El que corresponda al último dígito de la placa: [calendario](/calendario-matriculacion-vehicular/)."
---
## Mismas reglas, valores propios

Una motocicleta sigue el mismo ciclo anual que un automóvil: **el mes lo define el último dígito de la placa**, se pagan los mismos tipos de rubros, y en ciudades con revisión técnica obligatoria debe aprobarse la inspección. Lo que cambia son los **montos** y algunos detalles de la inspección.

## Qué se paga

| Rubro | Particularidad en motos |
|---|---|
| Impuesto a la propiedad | Según avalúo; muchas motos de bajo avalúo pagan poco |
| Impuesto ambiental | Según cilindraje |
| SPPAT | Tarifa propia para motocicletas |
| Tasas de matriculación | Según canal y ciudad |
| Revisión técnica | Tarifa para motos |

Para entender la lógica de cada línea, lee [valor a pagar](/valor-a-pagar-matricula/) y [qué es el SPPAT](/sppat/).

## Paso a paso

1. **Consulta multas** por placa.
2. **Revisión técnica** si tu ciudad la exige ([revisión técnica](/revision-tecnica-vehicular/)).
3. **Pago de rubros** en el canal oficial ([pago en línea](/pago-matricula-linea/)).
4. **Descarga o retiro** de la matrícula.

## Qué se revisa en una moto

- Luces y direccionales.
- Frenos delanteros y traseros.
- Neumáticos y suspensión.
- Cadena o transmisión.
- Escape y emisiones.
- Espejos y bocina.
- Identificación de placa y chasis.

## Consejos

- Lleva la moto limpia para ver los números de chasis y motor.
- Cambia llantas desgastadas antes de ir.
- Verifica que el casco y accesorios cumplan normas de uso aunque no formen parte de la revisión.
- Mantén la placa legible y bien sujeta; si se pierde, consulta [duplicado de placas](/duplicado-de-placas-vehiculares/).

## Multas más comunes en motos

Circular con matrícula vencida, sin casco o sin placa legible son infracciones frecuentes. Consulta el panorama en [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Compra de una moto usada

Haz el [cambio de propietario](/cambio-de-propietario-vehicular/) y pide un [CUV](/certificado-unico-vehicular/). En motos es frecuente encontrar cambios de motor o chasis sin registrar: desconfía si los números no coinciden.

## Motos nuevas

Siguen el flujo de [vehículos nuevos](/matriculacion-de-vehiculos-nuevos/), con factura, documentos de origen y asignación de placa.

## Motos eléctricas

Pueden tener beneficios tributarios. Revisa [eléctricos](/vehiculos-electricos-exoneracion-matricula/).

## Errores comunes

1. Pensar que, al ser pequeña, no necesita matrícula anual.
2. Ir a la revisión sin documentos.
3. No registrar cambios de motor.
4. Dejar la matrícula para diciembre.
<!-- PAGE:END -->

<!-- PAGE:START slug=sppat -->
---
title: "SPPAT: qué es, cuánto cuesta y cómo consultarlo"
description: "Qué es el SPPAT en Ecuador, a qué cubre, quién debe pagarlo, cuánto cuesta de referencia y cómo consultar su vigencia."
h1: "SPPAT en Ecuador: qué es y por qué es obligatorio"
short: "SPPAT"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "El SPPAT es el seguro público obligatorio de accidentes de tránsito. Todo vehículo matriculado debe pagarlo; cubre a las víctimas de accidentes sin importar el responsable y se cobra junto a la matrícula."
related: [valor-a-pagar-matricula, matriculacion-anual-vehicular, matricula-moto, multas-por-no-matricular-vehiculo, glosario-matriculacion-vehicular]
sources:
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
verify:
  - "Coberturas, montos asegurados y tarifa por clase de vehículo: confirmar con SPPAT."
faq:
  - q: "¿Quién debe pagar el SPPAT?"
    a: "Todo propietario de vehículo matriculado."
  - q: "¿Puedo matricular sin SPPAT?"
    a: "No. Forma parte de los rubros que se cancelan para completar la matrícula."
  - q: "¿Es lo mismo que un seguro privado?"
    a: "No. El SPPAT es un seguro público de accidentes; un seguro privado cubre otros riesgos, como daños al vehículo."
  - q: "¿Cómo sé si estoy al día?"
    a: "Consulta con la placa en el portal del SPPAT o en el estado de cuenta de matrícula."
---
## Qué es el SPPAT

El **Servicio Público para Pago de Accidentes de Tránsito (SPPAT)** es un seguro obligatorio que cubre a las personas afectadas por accidentes de tránsito. Funciona con el pago que hacen los propietarios de vehículos cada año al matricular. Su lógica es solidaria: protege a las víctimas aunque el responsable no tenga seguro o no sea identificado.

## Qué cubre

La cobertura se orienta a las personas afectadas por un accidente: atención médica, incapacidad, gastos funerarios, según los montos y condiciones que fija la norma. No cubre daños materiales al vehículo; para eso se contrata un seguro privado.

## Cuánto cuesta

La tarifa depende de la **clase y el uso** del vehículo. No existe un valor único para todos. Aparece como una línea del estado de cuenta de matrícula. Consulta la estructura en [valor a pagar](/valor-a-pagar-matricula/) y confirma el monto de tu clase en el canal oficial.

## Cómo se paga

Normalmente se paga junto con los demás rubros de la [matriculación anual](/matriculacion-anual-vehicular/). No necesitas hacer un trámite aparte, salvo que el canal de tu ciudad lo separe.

## Cómo consultar tu SPPAT

1. Ingresa al portal oficial con la placa.
2. Revisa el estado de vigencia.
3. Descarga el comprobante si lo necesitas.

## Qué pasa si no lo pagas

No podrás completar la matrícula y circularás sin cobertura obligatoria, lo cual puede traer sanciones. Si estás atrasado con la matrícula, lee [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## SPPAT en distintos tipos de vehículo

- **Autos y camionetas:** tarifa según clase.
- **Motos:** tarifa propia ([motos](/matricula-moto/)).
- **Transporte público y de carga:** tarifas específicas.
- **Vehículos nuevos:** se paga desde la primera matrícula ([vehículos nuevos](/matriculacion-de-vehiculos-nuevos/)).

## Mitos comunes

- «Si tengo seguro privado no necesito SPPAT»: el SPPAT es independiente y obligatorio.
- «Se paga solo si hay accidente»: se paga cada año con la matrícula.
- «Es un impuesto»: es un seguro público, aunque se cobra junto con otros rubros.

## Términos relacionados

Si necesitas aclarar siglas del proceso, consulta el [glosario](/glosario-matriculacion-vehicular/).
<!-- PAGE:END -->

<!-- PAGE:START slug=vehiculos-electricos-exoneracion-matricula -->
---
title: "Vehículos eléctricos: exoneración en la matrícula"
description: "Qué beneficios tienen los vehículos eléctricos en Ecuador al matricular: exoneración de impuestos, SPPAT y qué debes verificar con el SRI."
h1: "Vehículos eléctricos en Ecuador: beneficios al matricular"
short: "Eléctricos"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Los vehículos eléctricos tienen beneficios tributarios al matricular, como exoneración del impuesto a la propiedad y del SPPAT según la normativa vigente. Confirma tu caso con el SRI y el estado de cuenta antes de pagar."
related: [valor-a-pagar-matricula, exoneracion-de-impuestos-vehiculares, matriculacion-de-vehiculos-nuevos, sppat, matricula-moto]
sources:
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SPPAT", u: "https://www.sppat.gob.ec"}
verify:
  - "Alcance exacto de la exoneración EV (IPVM y SPPAT) y vigencia: confirmar con SRI/SPPAT y la normativa de 2026."
faq:
  - q: "¿Los eléctricos pagan matrícula?"
    a: "Pagan la parte que no está exonerada, como tasas y, si corresponde, revisión. El impuesto a la propiedad y el SPPAT tienen tratamiento especial según la norma vigente."
  - q: "¿La exoneración es automática?"
    a: "Puede aplicarse según el registro del vehículo como eléctrico. Si no se refleja en tu estado de cuenta, solicita revisión."
  - q: "¿Deben pasar la revisión técnica?"
    a: "Sí, con controles de seguridad; no tienen medición de gases de escape."
  - q: "¿Aplica a híbridos?"
    a: "El trato de los híbridos es distinto. Verifica en el SRI."
---
## Un trato tributario distinto

Los vehículos eléctricos reciben incentivos en Ecuador. En la práctica, para quien matricula, eso se nota en algunas líneas del estado de cuenta: el **impuesto a la propiedad de vehículos motorizados** y el **SPPAT** tienen tratamiento de exoneración según la normativa vigente en la fecha de revisión de esta página. El impuesto ambiental no aplica a un vehículo sin emisiones de escape.

Como las normas tributarias cambian, verifica el alcance exacto en el SRI y en tu estado de cuenta antes de pagar.

## Qué sigue pagándose

| Rubro | Situación en eléctricos |
|---|---|
| Impuesto a la propiedad | Exoneración según norma vigente |
| Impuesto ambiental | No aplica por no tener emisiones de combustión |
| SPPAT | Exoneración según norma vigente |
| Tasas de matriculación | Se pagan |
| Revisión técnica | Se realiza, sin control de gases |
| Multas | Se pagan como cualquier vehículo |

## Paso a paso

1. **Confirma que el vehículo esté registrado como eléctrico** en el sistema.
2. **Consulta el estado de cuenta** y verifica que la exoneración aparezca.
3. **Revisión técnica** si tu ciudad la exige ([revisión técnica](/revision-tecnica-vehicular/)).
4. **Paga lo que corresponda** y descarga la matrícula.

## Si la exoneración no aparece

- Verifica el tipo de combustible registrado.
- Revisa que el año y la clase sean correctos.
- Solicita al SRI o al canal de matrícula la revisión del beneficio.
- Si el registro está mal, corrígelo ([cambio de características](/cambio-de-caracteristicas-del-vehiculo/)).

## Comprar un eléctrico nuevo

El proceso de primera matrícula es el normal ([vehículos nuevos](/matriculacion-de-vehiculos-nuevos/)), con la ventaja de las exoneraciones. Pide al concesionario que detalle qué rubros incluye.

## Comprar un eléctrico usado

Haz el [cambio de propietario](/cambio-de-propietario-vehicular/) y revisa el CUV para asegurarte de que figure como eléctrico. Comprueba que los beneficios no tengan condiciones que dependan del primer propietario.

## Motos y otros vehículos eléctricos

Las motos eléctricas pueden tener un tratamiento similar. Mira [matrícula de motos](/matricula-moto/).

## Otras exoneraciones

Existen exoneraciones para otros grupos y situaciones: [exoneración de impuestos vehiculares](/exoneracion-de-impuestos-vehiculares/) y [rebaja para adultos mayores y personas con discapacidad](/rebaja-matricula-adultos-mayores-discapacidad/). Las normas pueden combinarse o no; consulta antes.

## Recomendación

Guarda la factura de compra y la ficha técnica que acredite que el vehículo es eléctrico. Son útiles para cualquier reclamo.
<!-- PAGE:END -->

<!-- PAGE:START slug=rebaja-matricula-adultos-mayores-discapacidad -->
---
title: "Rebaja de matrícula para adultos mayores y discapacidad"
description: "Cómo acceder a rebajas o exoneraciones en el impuesto vehicular en Ecuador para adultos mayores y personas con discapacidad: requisitos y pasos."
h1: "Rebaja de matrícula para adultos mayores y personas con discapacidad"
short: "Rebajas y beneficios"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Los adultos mayores y las personas con discapacidad pueden acceder a beneficios sobre el impuesto a la propiedad de un vehículo, con condiciones: titularidad, un solo vehículo y límites de avalúo. Debes solicitarlo y acreditar tu condición."
related: [exoneracion-de-impuestos-vehiculares, valor-a-pagar-matricula, matriculacion-anual-vehicular, vehiculos-electricos-exoneracion-matricula, contacto]
sources:
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
verify:
  - "Porcentajes de rebaja, límite de avalúo, número de vehículos y requisitos de acreditación: confirmar con SRI y normativa vigente."
faq:
  - q: "¿Quién califica como adulto mayor?"
    a: "La norma fija una edad mínima. Confirma el criterio vigente y acredítalo con tu cédula."
  - q: "¿Aplica a cualquier vehículo?"
    a: "Generalmente a un vehículo de uso personal, con límites de avalúo y titularidad. Consulta las condiciones actuales."
  - q: "¿Dónde se solicita?"
    a: "En el SRI. Una vez aprobado, se refleja en el cálculo del impuesto."
  - q: "¿Cubre otras tasas o multas?"
    a: "No. Se refiere al impuesto; tasas y multas se pagan según corresponda."
---
## Un beneficio que muchos no reclaman

El impuesto a la propiedad de vehículos motorizados contempla **rebajas o exoneraciones** para dos grupos: **adultos mayores** y **personas con discapacidad**. El beneficio no siempre se aplica solo: en la mayoría de casos debes **solicitarlo y acreditar** tu condición. Si nunca lo hiciste, puedes estar pagando de más.

## Quién puede acceder

| Grupo | Acreditación habitual |
|---|---|
| Adulto mayor | Cédula (edad) |
| Persona con discapacidad | Carné o certificado de discapacidad vigente |
| Representante o titular que cumple condiciones | Documentos de representación o titularidad |

Las condiciones precisas (porcentaje, límite de avalúo, cantidad de vehículos, tipo de uso) las fija la norma vigente. Aquí encontrarás el esquema; confirma los números en el SRI.

## Condiciones frecuentes

1. El vehículo debe estar **a nombre del beneficiario**.
2. Suele limitarse a **un vehículo** por beneficiario.
3. Existen **topes de avalúo**.
4. El vehículo debe ser de **uso personal**, no comercial.
5. Se requiere estar **al día** en otras obligaciones.

## Paso a paso

1. **Reúne documentos:** cédula, carné de discapacidad si aplica, matrícula.
2. **Consulta tu elegibilidad** en el canal del SRI.
3. **Presenta la solicitud** de beneficio.
4. **Espera la resolución** y verifica que se refleje en el estado de cuenta.
5. **Paga el saldo** y completa la [matrícula](/matriculacion-anual-vehicular/).

## Qué cambia en el total

El beneficio afecta el rubro del impuesto a la propiedad. Los demás componentes (SPPAT, tasas, revisión técnica, multas) se pagan como corresponda. Para ver la estructura completa, mira [valor a pagar](/valor-a-pagar-matricula/).

## Si tu solicitud es rechazada

Revisa el motivo: puede ser un tope de avalúo, titularidad o documentación. Corrige y presenta nuevamente, o apela dentro del plazo.

## Casos especiales

- **Vehículo adaptado.** Puede tener tratamiento adicional; documenta las adaptaciones.
- **Conductor distinto del titular.** Verifica si la norma exige que el beneficiario sea el titular.
- **Vehículo eléctrico.** Revisa si se acumulan beneficios: [eléctricos](/vehiculos-electricos-exoneracion-matricula/).
- **Otras exoneraciones.** [Exoneración de impuestos vehiculares](/exoneracion-de-impuestos-vehiculares/).

## Recomendaciones

Solicita el beneficio **antes** de tu mes de matriculación para evitar demoras ([calendario](/calendario-matriculacion-vehicular/)). Guarda la resolución del SRI. Y desconfía de quien cobre por «gestionar» el beneficio: es un trámite gratuito. Si tienes dudas, escríbenos desde [contacto](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=bloqueo-vehicular-desbloqueo -->
---
title: "Bloqueo vehicular: causas y cómo desbloquear"
description: "Qué es el bloqueo de un vehículo en Ecuador, por qué ocurre, cómo consultarlo y cómo solicitar el desbloqueo paso a paso."
h1: "Bloqueo vehicular en Ecuador: causas y desbloqueo"
short: "Bloqueo y desbloqueo"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Un bloqueo impide realizar trámites con el vehículo (matricular, traspasar, dar de baja). Se origina por deudas, órdenes judiciales o prohibiciones de enajenar. Para desbloquear, identifica la causa, cancela o resuelve y solicita el levantamiento ante la entidad que lo dispuso."
related: [certificado-unico-vehicular, multas-por-no-matricular-vehiculo, cambio-de-propietario-vehicular, consulta-multas-transito, baja-vehiculo]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Procedimiento de levantamiento por tipo de bloqueo y tasas: confirmar con la entidad que lo dispuso."
faq:
  - q: "¿Cómo sé si mi vehículo está bloqueado?"
    a: "Consulta con la placa en el portal oficial o solicita un [CUV](/certificado-unico-vehicular/)."
  - q: "¿Quién levanta el bloqueo?"
    a: "La entidad que lo dispuso: tránsito, un juez, una entidad financiera, según el caso."
  - q: "¿Puedo matricular un vehículo bloqueado?"
    a: "No hasta resolver el bloqueo."
  - q: "¿Cuánto tarda?"
    a: "Depende de la causa y la entidad. Un bloqueo por deuda se resuelve rápido tras el pago; uno judicial requiere orden de levantamiento."
---
## Qué es un bloqueo

Es una restricción registrada sobre el vehículo que **impide realizar ciertos trámites**: matricular, hacer el traspaso, dar de baja, cambiar características. Protege a terceros (acreedores, víctimas) y a la autoridad, pero puede sorprender a quien lo descubre al pagar.

## Causas frecuentes

| Causa | Quién la dispone |
|---|---|
| Multas de tránsito impagas | Autoridad de tránsito |
| Deudas tributarias o municipales | Entidad acreedora |
| Prenda o crédito vigente | Entidad financiera |
| Orden judicial | Juez |
| Prohibición de enajenar | Juez o autoridad |
| Denuncia de robo o ilícito | Fiscalía o policía |

## Cómo detectarlo

1. Consulta por placa en el portal oficial.
2. Revisa el [CUV](/certificado-unico-vehicular/).
3. Si el intento de pago muestra «no permitido», pide el motivo al canal.

## Paso a paso para desbloquear

1. **Identifica la causa** y quién lo dispuso.
2. **Resuelve el origen:** paga la multa, cancela la deuda o gestiona la orden.
3. **Solicita el levantamiento** a la entidad.
4. **Presenta documentos:** comprobante de pago, oficio de levantamiento, cédula.
5. **Espera la actualización** del sistema y verifica.
6. **Continúa con el trámite** que querías hacer.

## Si el bloqueo es por multas

Cancela las multas ([consulta de multas](/consulta-multas-transito/)) y verifica que el sistema se actualice. Si hay discrepancias, presenta el comprobante en el canal. El contexto de sanciones está en [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Si el bloqueo es por prenda

Solicita a la entidad financiera el **levantamiento de la prenda** una vez cancelado el crédito. Sin ese documento, el sistema mantendrá la restricción.

## Si el bloqueo es judicial

Se requiere una **orden del juez** que lo levante. Un abogado puede orientarte. No intentes resolverlo con intermediarios.

## Si compras un vehículo bloqueado

Nunca cierres la compra sin plan de levantamiento. Exige que el vendedor lo resuelva antes o pacta el pago contra la entrega del documento de levantamiento. Lee la guía de [cambio de propietario](/cambio-de-propietario-vehicular/).

## Si quieres dar de baja un vehículo bloqueado

Primero hay que levantar el bloqueo: [baja de vehículo](/baja-vehiculo/).

## Prevención

- Paga multas a tiempo.
- Haz el traspaso al vender.
- Consulta tu vehículo al menos una vez al año.
- Guarda comprobantes de pago por años.
<!-- PAGE:END -->

<!-- PAGE:START slug=turno-matriculacion-vehicular -->
---
title: "Turno de matriculación vehicular: cómo agendarlo"
description: "Cómo sacar turno para matriculación y revisión técnica vehicular en Ecuador: cuándo es necesario, canales y consejos para evitar filas."
h1: "Turno para matriculación y revisión técnica: cómo agendarlo"
short: "Turnos"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "El turno se agenda en el portal o canal de la entidad que gestiona la matriculación o la revisión técnica de tu ciudad. No todos los trámites lo exigen, pero conviene reservarlo con anticipación, sobre todo en tu mes y en diciembre."
related: [revision-tecnica-vehicular, matriculacion-anual-vehicular, calendario-matriculacion-vehicular, pago-matricula-linea, matriculacion-por-ciudad]
sources:
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
  - {t: "ATM Guayaquil", u: "https://www.atm.gob.ec"}
  - {t: "EMOV EP Cuenca", u: "https://www.emov.gob.ec"}
verify:
  - "Canal y condiciones de agendamiento por ciudad: confirmar en cada entidad."
faq:
  - q: "¿Es obligatorio el turno?"
    a: "Depende de la ciudad y del trámite. Algunos centros atienden sin cita, pero con espera larga."
  - q: "¿Qué hago si no consigo turno?"
    a: "Revisa nuevos cupos en horarios de la mañana y días intermedios. Si tu mes está por vencer, consulta si hay ampliación."
  - q: "¿Puedo cambiar o cancelar un turno?"
    a: "Sí, en general desde el mismo canal. Hazlo con anticipación."
  - q: "¿Me cobran por agendar?"
    a: "No debería. Desconfía de quien cobre por «conseguir» turnos."
---
## Cuándo necesitas turno

Hay dos situaciones en las que suele pedirse turno:

1. **Revisión técnica:** se agenda para ordenar el flujo en los centros ([revisión técnica](/revision-tecnica-vehicular/)).
2. **Trámites presenciales de matriculación:** retiro de documentos, adhesivos, traspasos o cambios de características.

Los trámites que se pagan y descargan en línea normalmente no necesitan turno ([pago en línea](/pago-matricula-linea/)).

## Cómo agendar

1. **Ubica el canal oficial** de tu ciudad: Quito (AMT), Guayaquil (ATM), Cuenca (EMOV EP) u otras ([matriculación por ciudad](/matriculacion-por-ciudad/)).
2. **Ingresa con tu placa y cédula.**
3. **Elige el servicio** (revisión técnica, matriculación, traspaso).
4. **Selecciona centro, fecha y hora.**
5. **Confirma y guarda** el comprobante del turno.
6. **Llega con anticipación** y con los documentos.

## Cuándo hay más demanda

- **En tu mes de matriculación**, sobre todo en el último tramo.
- **Diciembre**, por los rezagados.
- **Lunes y viernes**, que concentran visitas.

Mira el [calendario](/calendario-matriculacion-vehicular/) y ve con tiempo.

## Estrategias para conseguir turno

- Agenda con **uno o dos meses de anticipación**.
- Revisa el portal en horarios en que se liberan cupos.
- Considera un **centro alternativo** si es válido para tu vehículo.
- Si hay cancelaciones, revisa varias veces al día.

## Qué llevar el día del turno

- Comprobante del turno.
- Placa y matrícula anterior.
- Cédula del propietario o autorización firmada.
- Comprobantes de pago si el centro los pide.
- Vehículo en buen estado, si es para revisión.

## Qué hacer si pierdes el turno

Reagenda lo antes posible. Si el vencimiento de tu mes se acerca, consulta si hay turnos de emergencia o ampliaciones. No pagues a intermediarios.

## Errores comunes

1. No guardar el comprobante.
2. Ir a un centro distinto al del turno.
3. Olvidar la autorización cuando no va el propietario.
4. Agendar demasiado tarde.

## Trámites que suelen necesitar presencia

[Cambio de propietario](/cambio-de-propietario-vehicular/), [duplicado de matrícula](/duplicado-de-matricula-vehicular/), [duplicado de placas](/duplicado-de-placas-vehiculares/) y [cambio de características](/cambio-de-caracteristicas-del-vehiculo/).
<!-- PAGE:END -->

<!-- PAGE:START slug=duplicado-de-placas-vehiculares -->
---
title: "Duplicado de placas vehiculares: pasos y costos"
description: "Qué hacer si pierdes o te roban las placas de tu vehículo en Ecuador: denuncia, solicitud de duplicado, costos de referencia y plazos."
h1: "Duplicado de placas vehiculares en Ecuador"
short: "Duplicado de placas"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Si pierdes o te roban una o ambas placas, denuncia, solicita el duplicado en el canal de tránsito y paga la tasa. Como referencia, el duplicado cuesta alrededor de USD 23 por placa o USD 13 en otro caso, más una especie de USD 22. Confirma los valores."
related: [duplicado-de-matricula-vehicular, matriculacion-anual-vehicular, multas-por-no-matricular-vehiculo, bloqueo-vehicular-desbloqueo, tramites-vehiculares]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Costos de duplicado de placas (USD 23/13) y especie (USD 22), sanción por circular sin placas (30% SBU): confirmar."
faq:
  - q: "¿Puedo circular sin placas mientras llega el duplicado?"
    a: "No. Circular sin placas es una infracción. Pregunta por un permiso temporal: [permiso de circulación](/permiso-de-circulacion-temporal/)."
  - q: "¿Necesito denuncia?"
    a: "En caso de robo, sí. Para pérdida, el canal puede pedir una declaración."
  - q: "¿Cuánto tarda?"
    a: "Depende de la entidad y de la producción de placas. Consulta el estado en el canal."
  - q: "¿Cambian el número de placa?"
    a: "En general se repone con la misma numeración. Confirma con el canal."
---
## Cuándo se pide un duplicado

Las placas pueden perderse por robo, accidente o desprendimiento. También se reemplazan cuando están ilegibles o dañadas. Circular sin placas es una infracción, de modo que conviene actuar rápido.

## Pasos a seguir

1. **Si hay robo:** presenta la denuncia ante la autoridad.
2. **Si es pérdida:** prepara una declaración y verifica qué pide el canal.
3. **Reúne documentos:** matrícula, cédula, denuncia o declaración.
4. **Solicita el duplicado** en el canal oficial.
5. **Paga la tasa** y la especie.
6. **Retira las placas** o recíbelas según el procedimiento.

## Costos de referencia

| Concepto | Referencia |
|---|---|
| Duplicado de placa | USD 23 (según caso) o USD 13 |
| Especie | USD 22 |

Los valores dependen de la entidad y pueden cambiar. Confirma el monto exacto antes de pagar. Si tu vehículo tiene multas o bloqueos, resuélvelos primero ([bloqueo vehicular](/bloqueo-vehicular-desbloqueo/)).

## Mientras esperas

Pregunta si puedes obtener un **permiso temporal** para circular ([permiso de circulación temporal](/permiso-de-circulacion-temporal/)). Evita circular sin placas porque la sanción puede ser significativa. Mira [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Si las placas fueron robadas

Además de la denuncia, vigila que no se usen de forma indebida: reporta cualquier infracción que aparezca a tu nombre y guarda copia de la denuncia.

## Relación con la matrícula

Si se pierde la matrícula junto con las placas, tramita también el [duplicado de matrícula](/duplicado-de-matricula-vehicular/). Y si tu mes está cerca, mira el [calendario](/calendario-matriculacion-vehicular/).

## Recomendaciones

- Fija bien las placas con tornillos antirrobo.
- Toma una foto de las placas y la matrícula.
- No aceptes duplicados de intermediarios sin comprobante.

## Errores comunes

1. Circular sin placas esperando que nada pase.
2. No presentar la denuncia en caso de robo.
3. Pagar por canales no oficiales.
4. No verificar que los datos del duplicado sean los correctos.
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-de-vehiculos-importados -->
---
title: "Matriculación de vehículos importados en Ecuador"
description: "Qué trámites siguen los vehículos importados antes de matricularse en Ecuador: nacionalización, documentos, homologación, pagos y errores comunes."
h1: "Matriculación de vehículos importados en Ecuador"
short: "Vehículos importados"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Un vehículo importado debe completar primero su nacionalización y cumplir las condiciones técnicas exigidas; con los documentos aduaneros se registra y se matricula como un vehículo nuevo o usado, según el caso."
related: [matriculacion-de-vehiculos-nuevos, valor-a-pagar-matricula, certificado-unico-vehicular, permiso-de-circulacion-temporal, revision-tecnica-vehicular]
sources:
  - {t: "SENAE (Aduana del Ecuador)", u: "https://www.aduana.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Requisitos aduaneros vigentes (aranceles, restricciones por antigüedad, homologación): confirmar con SENAE y normativa de 2026."
faq:
  - q: "¿Puedo matricular el vehículo apenas llega?"
    a: "No. Primero debe completarse la nacionalización con la Aduana y obtener los documentos que acreditan la importación."
  - q: "¿Los importados pagan los mismos rubros?"
    a: "Pagan los de matrícula como cualquier vehículo, además de los tributos aduaneros previos."
  - q: "¿Se permiten vehículos usados importados?"
    a: "Las condiciones dependen de la normativa vigente de importación. Verifica antes de comprar."
  - q: "¿Necesito revisión técnica?"
    a: "Sí, en las ciudades que la exigen, salvo exoneración en primer periodo si aplica."
---
## Dos etapas distintas

Con un vehículo importado, el trámite se divide en dos: la **etapa aduanera** (nacionalización) y la **etapa de matriculación**. Hasta que la primera no termina, no se puede iniciar la segunda.

## Etapa 1: nacionalización

La Aduana (SENAE) verifica que el vehículo cumpla las condiciones de importación y liquida los tributos correspondientes. Al final entrega los documentos que acreditan la importación. Aquí es donde se define si el vehículo puede o no ingresar según la normativa vigente (antigüedad, tipo, normas técnicas).

## Etapa 2: matriculación

Con los documentos aduaneros se registra el vehículo en el sistema de tránsito y se asignan placas, siguiendo el proceso de [primera matrícula](/matriculacion-de-vehiculos-nuevos/).

| Documento | Para qué |
|---|---|
| Documentos aduaneros de nacionalización | Acreditan el ingreso legal |
| Factura de compra o título de propiedad | Acreditan la propiedad |
| Cédula del propietario | Identificación |
| Comprobantes de pago | Impuestos y tasas |
| Ficha técnica o certificado de homologación | Cuando el canal lo solicite |

## Paso a paso

1. **Verifica las reglas de importación** antes de comprar.
2. **Completa la nacionalización** con la Aduana.
3. **Reúne los documentos** y ubica el canal de tránsito de tu ciudad.
4. **Paga impuestos y tasas** ([valor a pagar](/valor-a-pagar-matricula/)).
5. **Revisión técnica** si corresponde ([RTV](/revision-tecnica-vehicular/)).
6. **Recibe placas y matrícula.**

## Mientras tanto: ¿puedo circular?

Sin placas no se puede circular. Pregunta por el [permiso de circulación temporal](/permiso-de-circulacion-temporal/).

## Riesgos al comprar un importado

- Documentos aduaneros incompletos.
- Números de chasis o motor que no coinciden.
- Vehículos que no cumplen la normativa técnica local.
- Intermediarios que prometen «nacionalizar» sin comprobantes.

Pide siempre un [CUV](/certificado-unico-vehicular/) si compras un importado ya matriculado.

## Errores comunes

1. Comprar sin verificar si el vehículo puede ingresar.
2. No guardar documentos aduaneros.
3. Pagar a gestores sin factura.
4. Intentar matricular antes de terminar la nacionalización.

## Vehículos eléctricos importados

Pueden tener beneficios; mira [eléctricos](/vehiculos-electricos-exoneracion-matricula/) y [exoneración de impuestos](/exoneracion-de-impuestos-vehiculares/).

## Después de matricular

Programa tu mes en el [calendario](/calendario-matriculacion-vehicular/) y guarda un archivo con todos los documentos de importación: se pedirán si vendes el vehículo.
<!-- PAGE:END -->

<!-- PAGE:START slug=permiso-de-circulacion-temporal -->
---
title: "Permiso de circulación temporal: qué es y cómo pedirlo"
description: "Qué es el permiso de circulación temporal en Ecuador, cuándo se usa, cuánto dura y cómo solicitarlo mientras llegan placas o documentos."
h1: "Permiso de circulación temporal en Ecuador"
short: "Permiso temporal"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "El permiso temporal autoriza a circular por un tiempo limitado mientras se completan documentos o placas. Se solicita en la entidad de tránsito con la documentación del vehículo, y su duración y costo dependen de la norma y la ciudad."
related: [matriculacion-de-vehiculos-nuevos, matriculacion-de-vehiculos-importados, duplicado-de-placas-vehiculares, multas-por-no-matricular-vehiculo, tramites-vehiculares]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Duración, costo y ámbito del permiso temporal vigente: confirmar con la entidad."
faq:
  - q: "¿Cuánto dura el permiso?"
    a: "Es por un tiempo limitado fijado por la norma y la entidad. Confirma el plazo actual."
  - q: "¿Reemplaza a la matrícula?"
    a: "No. Es una autorización transitoria mientras se completa el proceso."
  - q: "¿Puedo circular por todo el país?"
    a: "Depende de lo que autorice el permiso. Lee las condiciones al recibirlo."
  - q: "¿Se puede renovar?"
    a: "Solo bajo condiciones. Si el trámite principal se demora, consulta con la entidad."
---
## Para qué sirve

Hay momentos en que un vehículo necesita circular antes de tener sus documentos definitivos: recién comprado, recién importado, o mientras llegan las placas de un duplicado. El **permiso de circulación temporal** cubre ese lapso y evita multas por circular sin documentos.

## Casos en que se usa

| Situación | Por qué se requiere |
|---|---|
| Vehículo nuevo sin placas | Se completa el registro y la fabricación de placas ([vehículos nuevos](/matriculacion-de-vehiculos-nuevos/)) |
| Vehículo importado en proceso | Mientras se resuelve el registro ([importados](/matriculacion-de-vehiculos-importados/)) |
| Pérdida o robo de placas | Hasta recibir el duplicado ([duplicado de placas](/duplicado-de-placas-vehiculares/)) |
| Traslado para revisión | Para llegar al centro de inspección, en casos que la norma contemple |

## Cómo solicitarlo

1. **Reúne documentos:** factura o título, cédula, comprobante de pago si corresponde.
2. **Ingresa la solicitud** en el canal de la entidad de tránsito.
3. **Paga la tasa**, si existe.
4. **Recibe el permiso** y colócalo según las instrucciones.

## Condiciones habituales

- Tiene **fecha de vencimiento**.
- Puede limitarse a **rutas o fines específicos**.
- Debe llevarse **visible** en el vehículo.
- No exime del pago de impuestos ni de la matrícula definitiva.

## Qué pasa si vence

Circular con el permiso vencido equivale a hacerlo sin documentos. Puedes recibir una multa. Revisa el panorama en [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Consejos

- Pide el permiso **antes** de recoger el vehículo.
- Guarda copia digital.
- No lo prestes ni lo transfieras.
- Pon una alarma 5 días antes del vencimiento.

## Errores comunes

1. Circular sin permiso porque «es solo unas cuadras».
2. Confundir el permiso con una matrícula.
3. Perder la fecha de vencimiento.
4. Pagar a intermediarios.
<!-- PAGE:END -->

<!-- PAGE:START slug=exoneracion-de-impuestos-vehiculares -->
---
title: "Exoneración de impuestos vehiculares en Ecuador"
description: "Quiénes pueden exonerarse del impuesto vehicular en Ecuador: adultos mayores, discapacidad, eléctricos, y cómo solicitar el beneficio."
h1: "Exoneración de impuestos vehiculares en Ecuador"
short: "Exoneración de impuestos"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Existen exoneraciones o rebajas del impuesto a la propiedad de vehículos para ciertos grupos (adultos mayores, personas con discapacidad) y tipos de vehículo (eléctricos). Requieren solicitud y acreditación ante el SRI."
related: [rebaja-matricula-adultos-mayores-discapacidad, vehiculos-electricos-exoneracion-matricula, valor-a-pagar-matricula, matriculacion-anual-vehicular, contacto]
sources:
  - {t: "SRI", u: "https://www.sri.gob.ec"}
  - {t: "ANT", u: "https://www.ant.gob.ec"}
verify:
  - "Lista actual de exoneraciones, porcentajes y requisitos: confirmar con SRI."
faq:
  - q: "¿La exoneración es automática?"
    a: "No siempre. Muchas requieren solicitud y documentos."
  - q: "¿Cubre todos los rubros?"
    a: "No. Se refiere sobre todo al impuesto a la propiedad. Tasas, SPPAT y multas siguen su regla propia."
  - q: "¿Dónde solicito?"
    a: "En el SRI, siguiendo el procedimiento de beneficios tributarios."
  - q: "¿Puedo acumular beneficios?"
    a: "Depende de la norma. Consulta antes de asumir que se suman."
---
## Qué significa exonerar

Exonerar es dejar de pagar total o parcialmente un impuesto por disposición legal. En matriculación, el impuesto que más se exonera es el de **propiedad de vehículos motorizados**. Los beneficios se otorgan por **condición de la persona** o por **tipo de vehículo**.

## Beneficios más conocidos

| Beneficio | Se otorga por | Guía |
|---|---|---|
| Rebaja para adultos mayores | Edad del propietario | [Adultos mayores y discapacidad](/rebaja-matricula-adultos-mayores-discapacidad/) |
| Beneficio por discapacidad | Condición acreditada | [Adultos mayores y discapacidad](/rebaja-matricula-adultos-mayores-discapacidad/) |
| Vehículos eléctricos | Tipo de vehículo | [Eléctricos](/vehiculos-electricos-exoneracion-matricula/) |
| Otros casos previstos en la norma | Según el caso | Consultar al SRI |

## Cómo se solicita

1. **Verifica elegibilidad** con la norma vigente.
2. **Reúne documentos:** cédula, carné, factura, matrícula.
3. **Presenta la solicitud** en el SRI.
4. **Espera la resolución.**
5. **Confirma** que el beneficio se refleje antes de pagar.

## Qué sigue pagándose

La exoneración del impuesto no elimina otros cobros: tasas, SPPAT (salvo regla específica), revisión técnica, multas y recargos. El detalle está en [valor a pagar](/valor-a-pagar-matricula/).

## Cuándo solicitarlo

Antes de tu mes del [calendario](/calendario-matriculacion-vehicular/). Si lo haces tarde, puedes pagar primero y reclamar después, lo cual es más lento.

## Si te lo niegan

Revisa el motivo. Puede deberse a un tope de avalúo, titularidad o documentación. Corrige y reintenta, o apela dentro del plazo.

## Errores comunes

1. Suponer que el beneficio es automático.
2. Pagar a gestores por un trámite gratuito.
3. No actualizar datos del propietario.
4. Dejar vencer el carné de discapacidad.

## Dónde preguntar

Si no sabes qué beneficio aplica a tu caso, [escríbenos](/contacto/) y te orientamos a la fuente oficial; no podemos tramitar por ti.
<!-- PAGE:END -->

<!-- PAGE:START slug=cambio-de-servicio-vehicular -->
---
title: "Cambio de servicio vehicular: de particular a comercial"
description: "Cómo cambiar el servicio de un vehículo en Ecuador (particular a comercial o viceversa): requisitos, pasos, impactos en impuestos y errores comunes."
h1: "Cambio de servicio vehicular: particular, comercial y público"
short: "Cambio de servicio"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "El servicio indica el uso del vehículo (particular, comercial, público). Para cambiarlo debes solicitarlo a la entidad de tránsito, cumplir los requisitos del nuevo uso y asumir que impuestos, tasas y SPPAT pueden cambiar."
related: [cambio-de-caracteristicas-del-vehiculo, valor-a-pagar-matricula, sppat, matriculacion-anual-vehicular, cambio-de-propietario-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Requisitos y costo del cambio de servicio por entidad: confirmar."
faq:
  - q: "¿Qué cambia si paso a servicio comercial?"
    a: "Cambian algunas tasas, el SPPAT y puede exigirse documentación adicional (permisos operativos, por ejemplo)."
  - q: "¿Puedo usar mi auto particular para trabajar sin cambiar?"
    a: "El uso comercial formal requiere el servicio correspondiente. Consulta el riesgo de sanción."
  - q: "¿Cuánto tarda?"
    a: "Depende de la entidad y de la documentación."
  - q: "¿Se puede volver a particular?"
    a: "Sí, con el trámite inverso y cumpliendo las condiciones."
---
## Qué es el servicio

En la matrícula, el **servicio** define para qué se usa el vehículo: **particular** (uso personal), **comercial** (carga, transporte de pasajeros en esquemas autorizados, actividad económica) o **público** (taxis, buses, transporte autorizado). Cada servicio tiene reglas, tasas y seguros propios.

## Por qué cambiar

- Empiezas un negocio con un vehículo que antes era personal.
- Compras un vehículo que estaba registrado con otro uso.
- Dejas la actividad comercial y vuelves al uso personal.

## Qué suele cambiar

| Elemento | Posible impacto |
|---|---|
| Tasas de matriculación | Valores distintos según servicio |
| SPPAT | Tarifa por clase y uso |
| Impuestos | Pueden variar según tratamiento |
| Documentación | Permisos operativos para comercial o público |
| Revisión técnica | Parámetros por clase de servicio |

Revisa el efecto en tu caso en [valor a pagar](/valor-a-pagar-matricula/) y [SPPAT](/sppat/).

## Paso a paso

1. **Confirma los requisitos** del nuevo servicio con la entidad de tránsito.
2. **Reúne documentos:** matrícula, cédula o RUC, permisos operativos si aplica.
3. **Solicita el cambio** en el canal oficial.
4. **Inspección**, si el vehículo debe verificarse.
5. **Pago de tasas** del trámite.
6. **Actualización** del registro y la matrícula.

## Si el vehículo es de una empresa

Se necesitan los documentos de la persona jurídica, nombramiento del representante y, según el caso, permisos de la actividad. La compra por una empresa puede combinarse con el [cambio de propietario](/cambio-de-propietario-vehicular/).

## Cambios físicos asociados

Convertir un vehículo para uso comercial puede implicar modificaciones de carrocería o capacidad: [cambio de características](/cambio-de-caracteristicas-del-vehiculo/).

## Riesgos de no cambiar

Usar un vehículo particular para actividades comerciales sin el servicio correspondiente puede traer sanciones y problemas con seguros ante un siniestro.

## Errores comunes

1. Cambiar el servicio sin considerar el costo anual.
2. Olvidar permisos operativos.
3. No avisar a la aseguradora.
4. Dejar el trámite para el mes de matriculación.

## Después del cambio

Actualiza tus datos y programa tu renovación en el [calendario](/calendario-matriculacion-vehicular/). Para el ciclo anual completo, mira [matriculación anual](/matriculacion-anual-vehicular/).
<!-- PAGE:END -->

<!-- PAGE:START slug=duplicado-de-matricula-vehicular -->
---
title: "Duplicado de matrícula vehicular: cómo obtenerlo"
description: "Qué hacer si pierdes la matrícula de tu vehículo en Ecuador: requisitos, pasos, costos de referencia y errores comunes."
h1: "Duplicado de matrícula vehicular en Ecuador"
short: "Duplicado de matrícula"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Si perdiste o te robaron la matrícula, solicita un duplicado en el canal de tránsito con tu cédula y la placa. Si hay robo, anexa la denuncia. Paga la tasa y recibe el documento actualizado."
related: [duplicado-de-placas-vehiculares, matriculacion-anual-vehicular, certificado-unico-vehicular, cambio-de-propietario-vehicular, tramites-vehiculares]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Tasa del duplicado de matrícula y canal digital vigente: confirmar."
faq:
  - q: "¿Puedo circular sin la matrícula física?"
    a: "En muchos canales la matrícula digital es válida. Confirma que el tuyo la acepte."
  - q: "¿Necesito denuncia?"
    a: "En robo, sí. En pérdida, el canal puede pedir una declaración."
  - q: "¿Cuánto cuesta?"
    a: "La tasa varía por entidad. Consulta el valor actual."
  - q: "¿Cambia mi mes de matriculación?"
    a: "No. Depende del último dígito de la placa."
---
## Qué es y cuándo se pide

El duplicado es una **copia oficial** de la matrícula cuando el original se perdió, fue robado o se deterioró. Mantiene los mismos datos del vehículo y, si corresponde, los actualiza.

## Requisitos habituales

| Requisito | Detalle |
|---|---|
| Cédula del propietario | Identificación |
| Placa del vehículo | Para localizar el registro |
| Denuncia o declaración | Según causa de la pérdida |
| Pago de tasa | En el canal oficial |
| Vehículo sin bloqueos | Si hay bloqueo, resolverlo primero ([desbloqueo](/bloqueo-vehicular-desbloqueo/)) |

## Paso a paso

1. **Verifica** que el vehículo esté a tu nombre; si no, haz primero el [cambio de propietario](/cambio-de-propietario-vehicular/).
2. **Denuncia** si hubo robo.
3. **Solicita el duplicado** en el canal oficial.
4. **Paga la tasa.**
5. **Descarga o retira** el documento y verifica los datos.

## Matrícula digital

En varios canales, la matrícula puede descargarse en formato digital. Guarda una copia en tu teléfono y en la nube. Confirma que las autoridades de tu ciudad la acepten en controles.

## Si perdiste también las placas

Tramita el [duplicado de placas](/duplicado-de-placas-vehiculares/). Mientras tanto, consulta el [permiso temporal](/permiso-de-circulacion-temporal/).

## Si el duplicado coincide con tu mes

Aprovecha para hacer la [matriculación anual](/matriculacion-anual-vehicular/) y evitar viajes dobles.

## Errores comunes

1. Pagar por intermediarios.
2. No verificar los datos del duplicado.
3. Circular sin documentación sin saber si la digital es válida.
4. Olvidar denunciar en caso de robo.

## Consejos

Toma una foto de la matrícula y las placas cuando las tengas. Guarda tus documentos en un lugar seguro. Y si compras un usado, verifica que el [CUV](/certificado-unico-vehicular/) coincida con el documento.
<!-- PAGE:END -->

<!-- PAGE:START slug=baja-vehiculo -->
---
title: "Baja de un vehículo en Ecuador: requisitos y pasos"
description: "Cómo dar de baja un vehículo en Ecuador: cuándo procede, requisitos, pasos, deudas previas y efectos sobre la matrícula."
h1: "Baja de un vehículo en Ecuador: cuándo y cómo"
short: "Baja de vehículo"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "La baja retira un vehículo del parque automotor cuando ya no circulará (siniestro total, chatarrización, etc.). Requiere estar al día en deudas, presentar los documentos y solicitar el trámite en la entidad de tránsito."
related: [bloqueo-vehicular-desbloqueo, multas-por-no-matricular-vehiculo, certificado-unico-vehicular, tramites-vehiculares, cambio-de-propietario-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
verify:
  - "Causales de baja, requisitos y tasas vigentes: confirmar."
faq:
  - q: "¿La baja cancela mis deudas?"
    a: "No. Las deudas existentes deben resolverse; la baja no las elimina."
  - q: "¿Puedo reactivar un vehículo dado de baja?"
    a: "En general no. La baja suele ser definitiva; consulta casos especiales."
  - q: "¿Dejo de pagar matrícula con la baja?"
    a: "Sí, una vez registrada. Mientras no se complete, el vehículo sigue generando obligaciones."
  - q: "¿Puedo vender las piezas?"
    a: "Depende de la regulación. Pregunta antes."
---
## Qué es la baja

La **baja vehicular** es el trámite que retira definitivamente un vehículo del registro: deja de existir como vehículo habilitado para circular y dejas de pagar matrícula. Es distinto de simplemente dejar de usar el vehículo, que no frena ni el calendario ni las deudas.

## Cuándo procede

- **Siniestro con pérdida total.**
- **Deterioro irreparable.**
- **Chatarrización** o desarme autorizado.
- **Robo no recuperado**, según el procedimiento aplicable.

## Requisitos habituales

| Requisito | Detalle |
|---|---|
| Cédula del propietario | Identificación |
| Matrícula | Documento vigente |
| Informe técnico o peritaje | Según la causal |
| Certificado de no tener bloqueos | Si hay, resolverlo ([desbloqueo](/bloqueo-vehicular-desbloqueo/)) |
| Pago de deudas pendientes | Multas e impuestos |
| Denuncia | En caso de robo |

## Paso a paso

1. **Consulta deudas y bloqueos** ([consulta de multas](/consulta-multas-transito/)).
2. **Cancela lo pendiente.**
3. **Reúne el respaldo** de la causal (informe, peritaje, denuncia).
4. **Solicita la baja** en el canal oficial.
5. **Paga la tasa** del trámite.
6. **Recibe la resolución** y guárdala.

## Qué ocurre después

El vehículo deja de figurar como activo, ya no genera matrícula anual, y las placas se entregan o inutilizan según el procedimiento. Conserva la resolución de baja de por vida.

## Alternativa: vender en lugar de dar de baja

Si el vehículo aún tiene valor, vender y hacer el [traspaso](/cambio-de-propietario-vehicular/) puede ser mejor que dar de baja. Para vender, pide un [CUV](/certificado-unico-vehicular/) y resuelve deudas.

## Si no quieres dar de baja pero no lo usarás

Seguirás con obligaciones anuales y recargos por atraso ([multas por no matricular](/multas-por-no-matricular-vehiculo/)). Evalúa seriamente la baja si el vehículo no se recuperará.

## Errores comunes

1. Creer que dejar de usar el vehículo detiene las obligaciones.
2. Intentar la baja con bloqueos vigentes.
3. No guardar la resolución.
4. No cancelar el seguro privado tras la baja.
<!-- PAGE:END -->

<!-- PAGE:START slug=pago-matricula-linea -->
---
title: "Pago de matrícula en línea en Ecuador: guía segura"
description: "Cómo pagar la matrícula vehicular en línea en Ecuador de forma segura: canales oficiales, pasos, comprobantes y señales de fraude."
h1: "Pago de matrícula en línea: pasos y cómo evitar fraudes"
short: "Pago en línea"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Paga siempre desde el portal oficial de tu entidad (ANT, tu municipio o el SRI para impuestos) o desde las entidades financieras autorizadas. Verifica el valor, guarda el comprobante y desconfía de enlaces recibidos por mensajería."
related: [valor-a-pagar-matricula, matriculacion-anual-vehicular, consulta-multas-transito, fuentes-oficiales-ecuador, turno-matriculacion-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
verify:
  - "Canales de pago activos y entidades financieras autorizadas por ciudad: confirmar."
faq:
  - q: "¿Puedo pagar con tarjeta?"
    a: "Depende del canal. Los portales oficiales suelen aceptar varios medios; verifica en el tuyo."
  - q: "¿Cuándo se refleja el pago?"
    a: "Normalmente en minutos u horas. Guarda el comprobante hasta que aparezca."
  - q: "¿Cómo identifico un sitio falso?"
    a: "Revisa el dominio, que sea el oficial, y desconfía de enlaces por mensajes o redes sociales. Este sitio no recibe pagos."
  - q: "¿Qué hago si pagué y no aparece?"
    a: "Conserva el comprobante y reclama en el canal por donde pagaste."
---
## Importante: este sitio no recibe pagos

**matriculacionvehicular.com es informativo.** No cobramos ni gestionamos pagos. Todos los pagos se hacen en los portales oficiales o en entidades financieras autorizadas. Si alguien te pide dinero en nombre de este sitio, es una estafa: [repórtalo](/contacto/).

## Qué canales existen

| Canal | Para qué |
|---|---|
| Portal de la ANT o del municipio | Matrícula, tasas, multas |
| Portal del SRI | Impuesto a la propiedad vehicular |
| Entidades financieras autorizadas | Pago de rubros según convenio |
| Ventanillas presenciales | Cuando el trámite lo exige |

Los portales y canales cambian. Consulta [portales oficiales](/fuentes-oficiales-ecuador/).

## Paso a paso para pagar en línea

1. **Ingresa al portal oficial** escribiendo la dirección tú mismo.
2. **Consulta tu vehículo** con la placa.
3. **Revisa el detalle:** impuestos, tasas, SPPAT, multas ([valor a pagar](/valor-a-pagar-matricula/)).
4. **Cancela multas** pendientes si las hay ([consulta de multas](/consulta-multas-transito/)).
5. **Elige el medio de pago** y confirma.
6. **Guarda el comprobante** y descarga la matrícula.

## Señales de fraude

- Enlaces que llegan por WhatsApp, SMS o redes sociales con «descuentos».
- Dominios parecidos al oficial.
- Páginas que piden la clave completa de tu tarjeta o claves bancarias.
- Cobros mayores al total que aparece en el portal.
- Gestores que prometen «saltar la fila» o «reducir» multas.

## Qué hacer si caíste en un fraude

1. Avisa a tu banco de inmediato.
2. Cambia tus claves.
3. Guarda capturas y comprobantes.
4. Presenta una denuncia.

## Buenas prácticas

- Usa la red de tu casa u oficina, no Wi‑Fi público.
- Mantén tu navegador actualizado.
- Verifica que la dirección empiece con https y que sea la oficial.
- Consulta el valor antes de pagar y compáralo con la [estructura de rubros](/valor-a-pagar-matricula/).

## Después de pagar

Confirma que el estado del vehículo cambie a «matriculado» y descarga el documento. Si necesitas turno para retirar adhesivo o documentos, mira [turnos](/turno-matriculacion-vehicular/).

## Errores comunes

1. Pagar sin consultar multas.
2. Pagar dos veces por error.
3. No guardar el comprobante.
4. Pagar a un gestor sin factura.
<!-- PAGE:END -->

<!-- PAGE:START slug=consulta-multas-transito -->
---
title: "Consulta de multas de tránsito por placa en Ecuador"
description: "Cómo consultar multas de tránsito por placa en Ecuador: portales oficiales, qué información aparece, cómo pagarlas e impugnarlas."
h1: "Consulta de multas de tránsito por placa"
short: "Consulta de multas"
type: apoyo
schema: Article
updated: 2026-10-27
quick: "Consulta tus multas con la placa en el portal de la ANT o de tu municipio (AMT, ATM, EMOV). Verás si están pendientes, pagadas o en impugnación. Cancela las pendientes antes de matricular."
related: [multas-por-no-matricular-vehiculo, bloqueo-vehicular-desbloqueo, pago-matricula-linea, matriculacion-anual-vehicular, certificado-unico-vehicular]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "AMT Quito", u: "https://www.amt.gob.ec"}
  - {t: "ATM Guayaquil", u: "https://www.atm.gob.ec"}
  - {t: "EMOV EP Cuenca", u: "https://www.emov.gob.ec"}
verify:
  - "Portales de consulta vigentes por ciudad y datos requeridos: confirmar."
faq:
  - q: "¿Qué necesito para consultar?"
    a: "Normalmente la placa y, en algunos casos, la cédula del propietario."
  - q: "¿Las multas de otra ciudad aparecen?"
    a: "Depende de la integración de sistemas. Consulta en el portal nacional y en el municipal."
  - q: "¿Cómo impugno una multa?"
    a: "Dentro del plazo legal, ante la autoridad que la emitió, con pruebas."
  - q: "¿Se puede matricular con multas pendientes?"
    a: "No. Primero deben cancelarse."
---
## Por qué consultar antes de pagar

Una multa pendiente **bloquea el pago de la matrícula** y puede impedir otros trámites. Por eso la consulta de multas es el primer paso del [proceso anual](/matriculacion-anual-vehicular/) y también de cualquier compra de un vehículo usado.

## Dónde consultar

| Jurisdicción | Entidad de referencia |
|---|---|
| Nacional | ANT |
| Quito | AMT |
| Guayaquil | ATM |
| Cuenca | EMOV EP |
| Otras ciudades | Entidad de tránsito local |

Los enlaces a los portales están en [portales oficiales](/fuentes-oficiales-ecuador/).

## Paso a paso

1. Ingresa al portal oficial.
2. Selecciona la consulta de multas o infracciones.
3. Ingresa la placa (y los datos que pida).
4. Revisa el listado: fecha, tipo, valor y estado.
5. Descarga el detalle o el comprobante.
6. Paga lo pendiente por el canal habilitado ([pago en línea](/pago-matricula-linea/)).

## Cómo leer el resultado

- **Pendiente:** debes pagar.
- **Pagada:** ya cancelada; guarda el comprobante.
- **En impugnación:** en revisión; no se cobra hasta resolver.
- **Prescrita o anulada:** consulta con la entidad cómo se refleja.

## Si hay una multa que no reconoces

Verifica fecha, lugar y placa. Puede haber un error de lectura o una placa clonada. Solicita las pruebas (foto, registro) a la entidad y presenta tu impugnación en los plazos.

## Qué hacer con multas antiguas

Pregunta por el estado de cada una. Algunas pueden estar prescritas; otras acumulan recargos. No supongas: solicita la verificación formal.

## Relación con otros trámites

- Un vehículo con multas puede quedar bloqueado: [desbloqueo](/bloqueo-vehicular-desbloqueo/).
- Si compras un usado, pide el [CUV](/certificado-unico-vehicular/) además de la consulta.
- Para entender las sanciones por no matricular, lee [multas por no matricular](/multas-por-no-matricular-vehiculo/).

## Errores comunes

1. Consultar solo en un portal cuando hay varios.
2. No guardar el comprobante.
3. Pagar a intermediarios.
4. Ignorar multas «pequeñas» que bloquean la matrícula.
<!-- PAGE:END -->

<!-- PAGE:START slug=manual-paso-a-paso -->
---
title: "Manual paso a paso: matricular tu vehículo en Ecuador"
description: "Manual práctico con las etapas para matricular un vehículo en Ecuador: consulta, revisión técnica, pago y retiro, con una lista de verificación."
h1: "Manual paso a paso para matricular tu vehículo"
short: "Manual paso a paso"
type: apoyo
schema: HowTo
updated: 2026-10-27
quick: "Consulta tu mes, revisa multas, aprueba la revisión técnica si corresponde, paga los rubros en el canal oficial y descarga la matrícula. Esta guía te da el orden y los puntos de control."
related: [matriculacion-anual-vehicular, calendario-matriculacion-vehicular, valor-a-pagar-matricula, revision-tecnica-vehicular, pago-matricula-linea]
sources:
  - {t: "ANT", u: "https://www.ant.gob.ec"}
  - {t: "SRI", u: "https://www.sri.gob.ec"}
faq:
  - q: "¿Cuánto tiempo necesito para todo el proceso?"
    a: "Si todo está al día, un día. Con revisión técnica y turno, calcula varios días hábiles."
  - q: "¿Puedo hacerlo todo en línea?"
    a: "Muchos pasos sí; la revisión técnica es presencial. Confirma el canal de tu ciudad."
  - q: "¿Qué pasa si falla un paso?"
    a: "Resuélvelo antes de seguir: multas, bloqueos o revisión pendiente impiden completar el pago."
  - q: "¿Dónde está la versión detallada?"
    a: "En la guía de [matriculación anual](/matriculacion-anual-vehicular/)."
---
## Cómo usar este manual

Esta es la versión corta y ordenada. Cada etapa enlaza a una guía con más detalle. Marca cada punto a medida que avances.

## Etapa 0: prepara

- [ ] Identifica tu mes por el último dígito de la placa ([calendario](/calendario-matriculacion-vehicular/)).
- [ ] Ten a mano placa y cédula del propietario.
- [ ] Si compraste hace poco, verifica que el vehículo esté a tu nombre ([cambio de propietario](/cambio-de-propietario-vehicular/)).

## Etapa 1: consulta de deudas

- [ ] Consulta multas por placa ([consulta de multas](/consulta-multas-transito/)).
- [ ] Verifica que no existan bloqueos ([desbloqueo](/bloqueo-vehicular-desbloqueo/)).
- [ ] Cancela lo pendiente.

## Etapa 2: revisión técnica

- [ ] Averigua si tu ciudad la exige ([revisión técnica](/revision-tecnica-vehicular/)).
- [ ] Agenda turno si corresponde ([turnos](/turno-matriculacion-vehicular/)).
- [ ] Prepara el vehículo: luces, frenos, neumáticos.
- [ ] Aprueba la revisión y guarda el comprobante.

## Etapa 3: cálculo y pago

- [ ] Revisa el total y cada rubro ([valor a pagar](/valor-a-pagar-matricula/)).
- [ ] Aplica beneficios si te corresponden ([rebajas](/rebaja-matricula-adultos-mayores-discapacidad/)).
- [ ] Paga en el canal oficial ([pago en línea](/pago-matricula-linea/)).
- [ ] Guarda el comprobante.

## Etapa 4: documentos finales

- [ ] Descarga o retira la matrícula.
- [ ] Verifica placa, chasis y propietario.
- [ ] Retira el adhesivo si tu ciudad lo entrega.
- [ ] Archiva todo en digital.

## Si algo sale mal

| Problema | Qué hacer |
|---|---|
| No puedo pagar porque aparece una multa | Cancela la multa y reintenta |
| Mi vehículo está bloqueado | Identifica la causa y gestiona el levantamiento |
| Reprobé la revisión | Repara y haz la segunda revisión dentro del plazo |
| Perdí la matrícula | [Duplicado de matrícula](/duplicado-de-matricula-vehicular/) |
| Perdí las placas | [Duplicado de placas](/duplicado-de-placas-vehiculares/) |
| Me atrasé | [Multas por no matricular](/multas-por-no-matricular-vehiculo/) |

## Calendario de recordatorios

Pon tres alarmas: dos meses antes (revisión técnica), un mes antes (consulta de multas y turno) y una semana antes (pago). Así evitas recargos y filas.

## Después del trámite

Anota tu próxima fecha y guarda los comprobantes durante al menos un año. Si necesitas formularios, revisa [formatos descargables](/formatos-descargables/).
<!-- PAGE:END -->

<!-- PAGE:START slug=tramites-vehiculares -->
---
title: "Trámites vehiculares en Ecuador: índice completo"
description: "Todos los trámites vehiculares en Ecuador en un solo lugar: matrícula, traspaso, revisión técnica, duplicados, baja y más, con enlaces a cada guía."
h1: "Trámites vehiculares en Ecuador: elige el que necesitas"
short: "Trámites"
type: hub
schema: CollectionPage
updated: 2026-10-27
quick: "Este índice agrupa todos los trámites por situación: renovar, comprar o vender, perder documentos, cambiar datos y resolver problemas. Elige el tuyo y sigue la guía."
related: [matriculacion-por-ciudad, glosario-matriculacion-vehicular, fuentes-oficiales-ecuador, manual-paso-a-paso]
faq:
  - q: "¿Por dónde empiezo si no sé qué trámite necesito?"
    a: "Mira la sección «Mi situación» y elige la que se parezca a la tuya; cada guía te dice los pasos."
  - q: "¿Los trámites son iguales en todo el país?"
    a: "Las reglas de fondo sí; los canales, tarifas y centros dependen de la ciudad: [matriculación por ciudad](/matriculacion-por-ciudad/)."
---
## Mi situación

### Quiero renovar la matrícula
- [Matriculación anual](/matriculacion-anual-vehicular/): requisitos y pasos.
- [Calendario por dígito de placa](/calendario-matriculacion-vehicular/).
- [Valor a pagar](/valor-a-pagar-matricula/).
- [Revisión técnica](/revision-tecnica-vehicular/) y [turnos](/turno-matriculacion-vehicular/).
- [Pago en línea](/pago-matricula-linea/).
- [Manual paso a paso](/manual-paso-a-paso/).

### Compré o vendí un vehículo
- [Cambio de propietario](/cambio-de-propietario-vehicular/).
- [Certificado Único Vehicular](/certificado-unico-vehicular/).
- [Vehículos nuevos](/matriculacion-de-vehiculos-nuevos/).
- [Vehículos importados](/matriculacion-de-vehiculos-importados/).
- [Permiso de circulación temporal](/permiso-de-circulacion-temporal/).

### Perdí documentos o placas
- [Duplicado de matrícula](/duplicado-de-matricula-vehicular/).
- [Duplicado de placas](/duplicado-de-placas-vehiculares/).

### Quiero cambiar datos del vehículo
- [Cambio de características](/cambio-de-caracteristicas-del-vehiculo/).
- [Cambio de servicio](/cambio-de-servicio-vehicular/).

### Tengo multas o bloqueos
- [Consulta de multas](/consulta-multas-transito/).
- [Multas por no matricular](/multas-por-no-matricular-vehiculo/).
- [Bloqueo y desbloqueo](/bloqueo-vehicular-desbloqueo/).

### Quiero pagar menos o saber si tengo beneficios
- [Exoneración de impuestos](/exoneracion-de-impuestos-vehiculares/).
- [Adultos mayores y discapacidad](/rebaja-matricula-adultos-mayores-discapacidad/).
- [Vehículos eléctricos](/vehiculos-electricos-exoneracion-matricula/).
- [SPPAT](/sppat/).

### Ya no usaré el vehículo
- [Baja de vehículo](/baja-vehiculo/).

### Tengo una moto
- [Matrícula de moto](/matricula-moto/).

## Por tipo de actor

| Si eres... | Empieza por |
|---|---|
| Propietario que renueva | [Matriculación anual](/matriculacion-anual-vehicular/) |
| Comprador de usado | [CUV](/certificado-unico-vehicular/) y [cambio de propietario](/cambio-de-propietario-vehicular/) |
| Vendedor | [Cambio de propietario](/cambio-de-propietario-vehicular/) |
| Dueño de vehículo nuevo | [Vehículos nuevos](/matriculacion-de-vehiculos-nuevos/) |
| Persona que atrasó la matrícula | [Multas por no matricular](/multas-por-no-matricular-vehiculo/) |

## Ayuda para entender los términos

Si algún término técnico te frena, consulta el [glosario](/glosario-matriculacion-vehicular/). Y para saber dónde hacer cada gestión, revisa los [portales oficiales](/fuentes-oficiales-ecuador/).
<!-- PAGE:END -->

<!-- PAGE:START slug=matriculacion-por-ciudad -->
---
title: "Matriculación vehicular por ciudad en Ecuador"
description: "Guías por ciudad para matricular tu vehículo en Ecuador: Quito, Guayaquil, Cuenca, Ambato y Riobamba, con entidades, revisión técnica y pasos."
h1: "Matriculación vehicular por ciudad"
short: "Por ciudad"
type: hub
schema: CollectionPage
updated: 2026-10-27
quick: "El calendario por dígito es nacional, pero los canales, la revisión técnica y las tarifas dependen de quién gestiona el tránsito en tu ciudad. Elige la tuya."
related: [calendario-matriculacion-vehicular, revision-tecnica-vehicular, turno-matriculacion-vehicular, fuentes-oficiales-ecuador]
faq:
  - q: "¿Mi ciudad no aparece, qué hago?"
    a: "Sigue la guía de [matriculación anual](/matriculacion-anual-vehicular/) y confirma el canal en la entidad de tránsito de tu cantón. Si quieres que cubramos tu ciudad, [escríbenos](/contacto/)."
  - q: "¿Puedo matricular en otra ciudad?"
    a: "La matrícula se gestiona según el registro del vehículo. Consulta con la entidad si hay excepciones."
---
## Ciudades cubiertas

| Ciudad | Entidad de referencia | Guía de matrícula | Guía de revisión técnica |
|---|---|---|---|
| Quito | AMT | [Quito](/matriculacion-vehicular-quito/) | [RTV Quito](/revision-tecnica-vehicular-quito/) |
| Guayaquil | ATM | [Guayaquil](/matriculacion-vehicular-guayaquil/) | [RTV Guayaquil](/revision-tecnica-vehicular-guayaquil/) |
| Cuenca | EMOV EP | [Cuenca](/matriculacion-vehicular-cuenca/) | [RTV Cuenca](/revision-tecnica-vehicular-cuenca/) |
| Ambato | Entidad local de tránsito | [Ambato](/matriculacion-vehicular-ambato/) | [Guía general](/revision-tecnica-vehicular/) |
| Riobamba | Entidad local de tránsito | [Riobamba](/matriculacion-vehicular-riobamba/) | [Guía general](/revision-tecnica-vehicular/) |

## Qué es igual en todo el país

- El **mes** de matriculación según el último dígito de la placa ([calendario](/calendario-matriculacion-vehicular/)).
- La **estructura de pagos**: impuesto a la propiedad, ambiental, SPPAT y tasas ([valor a pagar](/valor-a-pagar-matricula/)).
- La necesidad de **consultar multas** antes de pagar ([consulta de multas](/consulta-multas-transito/)).

## Qué cambia entre ciudades

- La **entidad** que gestiona el trámite.
- La **revisión técnica**: centros, tarifas y plazos ([revisión técnica](/revision-tecnica-vehicular/)).
- Los **turnos** y canales de atención ([turnos](/turno-matriculacion-vehicular/)).
- Las **tasas locales**.

## Cómo usar estas guías

1. Elige tu ciudad en la tabla.
2. Revisa la sección de pasos y las tarifas de referencia.
3. Confirma en el portal oficial antes de pagar.
4. Si ves un dato desactualizado, [avísanos](/contacto/).

## Ciudades en preparación

Estamos ampliando la cobertura. Solo publicamos una guía cuando podemos respaldar los datos con una fuente oficial; mientras tanto, la [guía general](/matriculacion-anual-vehicular/) aplica a cualquier ciudad.
<!-- PAGE:END -->

<!-- PAGE:START slug=blog -->
---
title: "Novedades de matriculación vehicular en Ecuador"
description: "Cambios y novedades sobre matriculación, revisión técnica y trámites vehiculares en Ecuador, con fecha y fuente de cada actualización."
h1: "Novedades de matriculación y trámites vehiculares"
short: "Novedades"
type: hub
schema: CollectionPage
updated: 2026-10-27
quick: "Aquí registramos los cambios relevantes con fecha y fuente. Si buscas la guía completa de un tema, ve directo a la página correspondiente."
related: [calendario-matriculacion-vehicular, revision-tecnica-vehicular-quito, metodologia-editorial, tramites-vehiculares]
faq:
  - q: "¿Cada cuánto se actualiza esta sección?"
    a: "Cuando hay un cambio verificable en normas, calendarios o tarifas, y en revisiones mensuales."
  - q: "¿Dónde veo la fecha de revisión de cada guía?"
    a: "En la parte superior de cada página, bajo el título."
---
## Registro de novedades

| Fecha | Novedad | Fuente | Guía relacionada |
|---|---|---|---|
| 2026-10-27 | Revisión general de contenidos y calendario al mes de octubre | Interna | [Calendario](/calendario-matriculacion-vehicular/) |
| 2026-10-22 | Actualización de la hoja de tarifas municipal de revisión técnica en Quito | Municipio de Quito | [RTV Quito](/revision-tecnica-vehicular-quito/) |
| 2026-03-09 | Reactivación del servicio en 127 municipios autorizados tras el incidente del sistema AXIS 4.0 de la ANT | Prensa regional | [Matriculación en Ambato](/matriculacion-vehicular-ambato/) |
| 2026-03-03 | Quito: placas 1 y 2 inician la revisión; la placa 1 queda libre de la multa de USD 25 | Quito Informa | [Matriculación en Quito](/matriculacion-vehicular-quito/) |
| 2026-03-02 | Guayaquil: se suspenden los turnos en línea de revisión técnica | Diario Expreso | [RTV Guayaquil](/revision-tecnica-vehicular-guayaquil/) |
| 2026-01-19 | Quito: centros de revisión y matriculación atienden con turno; la matrícula se emite en el mismo centro al aprobar | Primicias con datos de la AMT | [RTV Quito](/revision-tecnica-vehicular-quito/) |
| 2026-01-19 | Guayaquil: tarifario 2026 de revisión técnica y tasas (memorando EPMTMG-DFI-2026-0143-M) | ATM Guayaquil | [RTV Guayaquil](/revision-tecnica-vehicular-guayaquil/) |

Esta tabla crece con cada cambio comprobado. No publicamos rumores ni información sin fuente.

## Guías más consultadas

- [Calendario de matriculación](/calendario-matriculacion-vehicular/)
- [Valor a pagar](/valor-a-pagar-matricula/)
- [Revisión técnica](/revision-tecnica-vehicular/)
- [Multas por no matricular](/multas-por-no-matricular-vehiculo/)
- [Cambio de propietario](/cambio-de-propietario-vehicular/)

## Cómo trabajamos las actualizaciones

Cada cambio pasa por tres controles: verificamos la fuente oficial, actualizamos la guía correspondiente y registramos la fecha. El método está en [metodología editorial](/metodologia-editorial/).

## Cómo avisarnos de un cambio

Si detectas un cambio de tarifas, calendario o procedimiento, envíanos el enlace oficial desde [contacto](/contacto/). Lo revisamos y, si es correcto, actualizamos la guía con su fecha.

## Todos los trámites

Para ver el listado completo por situación, entra a [trámites vehiculares](/tramites-vehiculares/).
<!-- PAGE:END -->

<!-- PAGE:START slug=formatos-descargables -->
---
title: "Formatos y modelos para trámites vehiculares"
description: "Modelos de contrato de compraventa de vehículo y de autorización para trámites en Ecuador, con indicaciones para completarlos."
h1: "Formatos y modelos para trámites vehiculares"
short: "Formatos"
type: hub
schema: CollectionPage
updated: 2026-10-27
quick: "Los formularios oficiales se obtienen en los portales de tránsito. Aquí encuentras modelos de texto orientativos (compraventa y autorización) que puedes adaptar. Revísalos con un profesional si el caso es complejo."
related: [cambio-de-propietario-vehicular, manual-paso-a-paso, certificado-unico-vehicular, tramites-vehiculares]
faq:
  - q: "¿Estos modelos tienen validez legal?"
    a: "Son orientativos. La validez depende de que cumplan los requisitos de la entidad y, si corresponde, del reconocimiento de firmas."
  - q: "¿Dónde consigo los formularios oficiales?"
    a: "En los portales de la ANT o de tu municipio: [portales oficiales](/fuentes-oficiales-ecuador/)."
---
## Aviso

Estos modelos son **orientativos**. No sustituyen asesoría legal ni los formularios oficiales cuando el trámite los exige. Revisa los requisitos en la [guía de cambio de propietario](/cambio-de-propietario-vehicular/).

## Modelo de contrato de compraventa de vehículo

> **CONTRATO DE COMPRAVENTA DE VEHÍCULO**
>
> En la ciudad de ______, a los ___ días del mes de ______ de 20__, comparecen: por una parte, ______ (nombres completos), con cédula N.º ______, en adelante **EL VENDEDOR**; y por otra, ______ (nombres completos), con cédula N.º ______, en adelante **EL COMPRADOR**.
>
> **Primera. Objeto.** EL VENDEDOR vende a EL COMPRADOR el vehículo con las siguientes características: marca ______, modelo ______, año ______, color ______, placa ______, chasis N.º ______, motor N.º ______.
>
> **Segunda. Precio y forma de pago.** El precio es de USD ______, pagado de la siguiente forma: ______.
>
> **Tercera. Estado del vehículo.** EL VENDEDOR declara que el vehículo está libre de gravámenes, prohibiciones de enajenar y deudas de tránsito, salvo lo indicado: ______.
>
> **Cuarta. Entrega.** La entrega se realiza el ___ de ______ de 20__, con el kilometraje de ______.
>
> **Quinta. Traspaso.** Los costos del traspaso serán asumidos por ______. Las partes se comprometen a completar el traspaso dentro del plazo legal.
>
> **Sexta. Responsabilidades.** Desde la entrega, las multas y responsabilidades por el uso del vehículo corresponden a EL COMPRADOR, y las anteriores a EL VENDEDOR.
>
> Firman las partes en señal de conformidad.
>
> ______________________ &nbsp;&nbsp;&nbsp; ______________________
> EL VENDEDOR &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; EL COMPRADOR

### Cómo completarlo

1. Copia los datos **exactos** de la matrícula y del vehículo (placa, chasis, motor).
2. Describe la forma de pago con precisión (transferencia, cheque, cuotas).
3. Indica quién paga el traspaso.
4. Pide que ambos firmen y, si el trámite lo exige, reconoce las firmas ante notario.
5. Guarda una copia firmada cada parte.

## Modelo de autorización para trámites

> **AUTORIZACIÓN**
>
> Yo, ______, con cédula N.º ______, propietario del vehículo placa ______, autorizo a ______, con cédula N.º ______, para que realice en mi nombre el siguiente trámite: ______ (matriculación / revisión técnica / retiro de documentos), ante ______ (entidad).
>
> La presente autorización es válida hasta el ___ de ______ de 20__.
>
> Lugar y fecha: ______
>
> Firma: ______________________

### Cuándo se usa

Cuando el propietario no puede asistir. Algunas entidades piden copia de la cédula de ambos o reconocimiento de firma.

## Lista de documentos para tus trámites

| Trámite | Documentos clave |
|---|---|
| Matrícula anual | Placa, cédula, comprobantes ([matriculación anual](/matriculacion-anual-vehicular/)) |
| Traspaso | Contrato, cédulas, comprobantes ([traspaso](/cambio-de-propietario-vehicular/)) |
| Duplicado de matrícula | Cédula, denuncia ([duplicado](/duplicado-de-matricula-vehicular/)) |
| Duplicado de placas | Cédula, denuncia ([placas](/duplicado-de-placas-vehiculares/)) |
| Baja | Informe técnico, cédula ([baja](/baja-vehiculo/)) |

## Recomendaciones

Antes de firmar cualquier documento, lee todo y confirma datos. Si el vehículo tiene prenda o bloqueo, resuelve eso primero ([desbloqueo](/bloqueo-vehicular-desbloqueo/)).
<!-- PAGE:END -->

<!-- PAGE:START slug=glosario-matriculacion-vehicular -->
---
title: "Glosario de matriculación vehicular en Ecuador"
description: "Definiciones breves de términos de matriculación vehicular en Ecuador: SPPAT, RTV, CUV, avalúo, SBU, IPVM, bloqueo, baja y más."
h1: "Glosario de matriculación vehicular"
short: "Glosario"
type: hub
schema: WebPage
updated: 2026-10-27
quick: "Definiciones de una línea para los términos que más aparecen al matricular: SPPAT, RTV, CUV, avalúo, SBU, bloqueo y otros."
related: [tramites-vehiculares, valor-a-pagar-matricula, sppat, certificado-unico-vehicular]
faq:
  - q: "¿Falta un término?"
    a: "Envíalo desde [contacto](/contacto/) y lo añadimos con su fuente."
---
## Términos A–Z

**Adhesivo de revisión.** Etiqueta que acredita que el vehículo aprobó la revisión técnica. Ver [revisión técnica](/revision-tecnica-vehicular/).

**ANT.** Agencia Nacional de Tránsito, entidad rectora del tránsito terrestre en Ecuador.

**AMT.** Agencia Metropolitana de Tránsito de Quito. Ver [Quito](/matriculacion-vehicular-quito/).

**ATM.** Empresa Pública Municipal de Tránsito y Movilidad de Guayaquil EP. Ver [Guayaquil](/matriculacion-vehicular-guayaquil/).

**Avalúo.** Valor del vehículo que sirve de base para calcular el impuesto a la propiedad. Ver [valor a pagar](/valor-a-pagar-matricula/).

**Baja.** Retiro definitivo de un vehículo del registro. Ver [baja](/baja-vehiculo/).

**Bloqueo.** Restricción que impide realizar trámites con el vehículo. Ver [bloqueo vehicular](/bloqueo-vehicular-desbloqueo/).

**CUV.** Certificado Único Vehicular. Ver [CUV](/certificado-unico-vehicular/).

**EMOV EP.** Empresa Pública de Movilidad, Tránsito y Transporte de Cuenca. Ver [Cuenca](/matriculacion-vehicular-cuenca/).

**Impuesto ambiental.** Impuesto a la contaminación vehicular, según cilindraje y antigüedad.

**IPVM / impuesto a la propiedad vehicular.** Impuesto anual sobre el avalúo del vehículo, administrado por el SRI.

**Matrícula.** Documento que habilita al vehículo a circular. Ver [matriculación anual](/matriculacion-anual-vehicular/).

**Mora.** Atraso en el pago, que genera recargos. Ver [multas por no matricular](/multas-por-no-matricular-vehiculo/).

**Placa.** Identificación alfanumérica del vehículo; el último dígito define el mes de matrícula. Ver [calendario](/calendario-matriculacion-vehicular/).

**Prenda.** Garantía sobre el vehículo por un crédito; puede generar un bloqueo hasta su levantamiento.

**Recargo.** Valor adicional por pago fuera de plazo.

**RTV.** Revisión técnica vehicular. Ver [RTV](/revision-tecnica-vehicular/).

**SBU.** Salario Básico Unificado; base para calcular el monto de muchas multas.

**Servicio.** Uso del vehículo (particular, comercial, público). Ver [cambio de servicio](/cambio-de-servicio-vehicular/).

**SPPAT.** Servicio Público para Pago de Accidentes de Tránsito. Ver [SPPAT](/sppat/).

**SRI.** Servicio de Rentas Internas.

**Traspaso.** Cambio de propietario. Ver [cambio de propietario](/cambio-de-propietario-vehicular/).
<!-- PAGE:END -->

<!-- PAGE:START slug=fuentes-oficiales-ecuador -->
---
title: "Portales oficiales de tránsito y matriculación en Ecuador"
description: "Enlaces a los portales oficiales para matricular, pagar impuestos, consultar multas y agendar revisión técnica en Ecuador."
h1: "Portales oficiales de tránsito y matriculación"
short: "Portales oficiales"
type: confianza
schema: WebPage
updated: 2026-10-27
quick: "Este sitio es informativo. Para pagar o tramitar, usa únicamente los portales oficiales listados aquí."
related: [pago-matricula-linea, consulta-multas-transito, matriculacion-por-ciudad, metodologia-editorial]
faq:
  - q: "¿Por qué debo usar solo portales oficiales?"
    a: "Para evitar fraudes y cobros indebidos. Este sitio no gestiona pagos."
---
## Portales de referencia

| Entidad | Para qué sirve | Enlace |
|---|---|---|
| ANT | Normativa y servicios de tránsito | [ant.gob.ec](https://www.ant.gob.ec) |
| SRI | Impuesto a la propiedad vehicular y beneficios | [sri.gob.ec](https://www.sri.gob.ec) |
| AMT Quito | Matriculación, revisión y multas en Quito | [amt.gob.ec](https://www.amt.gob.ec) |
| ATM Guayaquil | Trámites de tránsito en Guayaquil | [atm.gob.ec](https://www.atm.gob.ec) |
| EMOV EP Cuenca | Movilidad y revisión técnica en Cuenca | [emov.gob.ec](https://www.emov.gob.ec) |
| SPPAT | Seguro público de accidentes de tránsito | [sppat.gob.ec](https://www.sppat.gob.ec) |
| SENAE | Aduana, para vehículos importados | [aduana.gob.ec](https://www.aduana.gob.ec) |

## Cómo reconocer un portal oficial

- El dominio termina en **.gob.ec**.
- Escribe la dirección tú mismo, no uses enlaces recibidos por mensajes.
- Verifica el candado y https.
- Desconfía de portales que cobren por «consultas».

Más consejos en [pago en línea](/pago-matricula-linea/).

## Qué hacemos con estas fuentes

Cada guía cita las fuentes en la parte inferior y marca los datos que debes confirmar. Conoce el proceso en [metodología editorial](/metodologia-editorial/).
<!-- PAGE:END -->

<!-- PAGE:START slug=sobre-nosotros -->
---
title: "Sobre este sitio | Matriculación Vehicular Ecuador"
description: "Quiénes somos, para qué existe este sitio informativo sobre matriculación vehicular en Ecuador y cómo mantenemos la información actualizada."
h1: "Sobre este sitio"
short: "Sobre nosotros"
type: confianza
schema: WebPage
updated: 2026-10-27
quick: "Somos una guía informativa independiente sobre matriculación y trámites vehiculares en Ecuador. No somos una entidad oficial ni gestionamos trámites."
related: [metodologia-editorial, fuentes-oficiales-ecuador, contacto, aviso-legal]
faq:
  - q: "¿Son una entidad del gobierno?"
    a: "No. Somos un sitio informativo independiente."
  - q: "¿Pueden tramitar mi matrícula?"
    a: "No. Solo explicamos el proceso y te enlazamos a los portales oficiales."
---
## Qué es este sitio

**matriculacionvehicular.com** explica en lenguaje simple cómo matricular un vehículo y realizar trámites relacionados en Ecuador. Nuestro objetivo es que encuentres rápido tu mes, el valor aproximado a pagar y los pasos a seguir, siempre con el portal oficial a mano.

## Qué no somos

- No somos la ANT, el SRI ni ningún municipio.
- No cobramos ni gestionamos pagos.
- No ofrecemos servicios de gestoría.

## Cómo financiamos el sitio

El sitio se sostiene con publicidad (Google AdSense). Los anuncios no influyen en el contenido. Más información en la [política de privacidad](/politica-de-privacidad/).

## Compromisos editoriales

1. Citar fuentes oficiales.
2. Mostrar la fecha de revisión en cada guía.
3. Marcar como referencia los montos que cambian.
4. Corregir errores con rapidez.

El método completo está en [metodología editorial](/metodologia-editorial/).

## Cómo contactarnos

Si encuentras un error o quieres sugerir una guía, escribe desde [contacto](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=metodologia-editorial -->
---
title: "Metodología editorial | Matriculación Vehicular"
description: "Cómo investigamos, verificamos y actualizamos las guías de matriculación vehicular en Ecuador: fuentes, fechas, correcciones y publicidad."
h1: "Metodología editorial"
short: "Metodología"
type: confianza
schema: WebPage
updated: 2026-10-27
quick: "Cada guía parte de fuentes oficiales, muestra su fecha de revisión, marca los montos que debes confirmar y se corrige cuando algo cambia."
related: [sobre-nosotros, fuentes-oficiales-ecuador, blog, contacto]
faq:
  - q: "¿Cada cuánto revisan las guías?"
    a: "Mensualmente, y de inmediato cuando hay un cambio verificable."
  - q: "¿Cómo reportan un error?"
    a: "Desde [contacto](/contacto/); lo verificamos y publicamos la corrección con fecha."
---
## Principios

1. **Fuente primero.** Priorizamos normativa y portales oficiales sobre notas de prensa y foros.
2. **Fecha visible.** Cada guía indica cuándo fue revisada por última vez.
3. **Lo incierto se marca.** Cuando un monto depende de tablas cambiantes, lo presentamos como referencia.
4. **Utilidad antes que volumen.** No publicamos páginas que no resuelvan una necesidad real.

## Proceso

1. Identificamos la pregunta del usuario.
2. Buscamos la fuente oficial.
3. Redactamos en lenguaje claro, con pasos y ejemplos.
4. Añadimos preguntas frecuentes y enlaces a guías relacionadas.
5. Revisamos fechas, cifras y enlaces.
6. Publicamos con fecha y registramos la novedad en [novedades](/blog/).

## Cómo tratamos las cifras

Los valores de impuestos, tasas y multas cambian. Los mostramos como referencia con su fuente y te remitimos a la consulta oficial. Los porcentajes sobre el SBU se actualizan cuando cambia el SBU.

## Publicidad

Mostramos anuncios de Google AdSense. No aceptamos contenido pagado que condicione la información. Las páginas legales y de contacto no muestran anuncios.

## Correcciones

Si algo es incorrecto, lo corregimos y actualizamos la fecha. Puedes avisarnos desde [contacto](/contacto/).

## Independencia

No tenemos vínculo con entidades de gobierno. Consulta [sobre este sitio](/sobre-nosotros/) y el [aviso legal](/aviso-legal/).
<!-- PAGE:END -->

<!-- PAGE:START slug=contacto -->
---
title: "Contacto | Matriculación Vehicular Ecuador"
description: "Escríbenos para reportar un error, sugerir una guía o consultar sobre el sitio. No tramitamos matrículas ni cobramos servicios."
h1: "Contacto"
short: "Contacto"
type: confianza
schema: WebPage
updated: 2026-10-27
quick: "Escríbenos para reportar errores o sugerir guías. No tramitamos matrículas ni gestionamos pagos."
related: [sobre-nosotros, metodologia-editorial, fuentes-oficiales-ecuador]
verify:
  - "Crear la cuenta de correo publicada (contacto@matriculacionvehicular.com) antes del lanzamiento o sustituirla por la real."
faq:
  - q: "¿Pueden ayudarme con mi trámite?"
    a: "Solo con orientación general. Para trámites usa los [portales oficiales](/fuentes-oficiales-ecuador/)."
---
## Escríbenos

Correo: **contacto@matriculacionvehicular.com**

Responderemos a consultas sobre el contenido del sitio, errores y sugerencias.

## Qué puedes enviarnos

- Reportes de datos desactualizados (con el enlace oficial).
- Sugerencias de nuevas guías.
- Consultas sobre publicidad o privacidad.

## Qué no podemos hacer

- Tramitar matrículas o pagos.
- Consultar multas o datos de tu vehículo.
- Dar asesoría legal.

## Aviso

Nunca te pediremos datos bancarios ni contraseñas. Si alguien lo hace usando nuestro nombre, es un fraude: reenvíanos el mensaje. Consulta cómo identificar portales oficiales en [portales oficiales](/fuentes-oficiales-ecuador/).
<!-- PAGE:END -->

<!-- PAGE:START slug=politica-de-privacidad -->
---
title: "Política de privacidad | Matriculación Vehicular"
description: "Cómo tratamos los datos en matriculacionvehicular.com: analítica, publicidad de Google AdSense, cookies y derechos de los usuarios."
h1: "Política de privacidad"
short: "Privacidad"
type: confianza
schema: WebPage
updated: 2026-10-27
show_date: true
related: [politica-de-cookies, aviso-legal, contacto]
faq:
  - q: "¿Recopilan datos de mi vehículo?"
    a: "No. No pedimos ni almacenamos placas ni datos personales de trámites."
---
## Quiénes somos

Este sitio informativo es operado por su editor independiente. Puedes contactarnos en [contacto](/contacto/).

## Qué datos tratamos

- **Datos de navegación** mediante analítica (Google Analytics 4): páginas visitadas, dispositivo, país aproximado.
- **Datos de publicidad** mediante Google AdSense: identificadores y cookies usados para mostrar anuncios.
- **Mensajes** que nos envíes por correo.

No pedimos datos de vehículos ni realizamos pagos.

## Finalidades

1. Mejorar el contenido y el rendimiento del sitio.
2. Mostrar publicidad que financia el sitio.
3. Responder consultas.

## Cookies

Usamos cookies propias y de terceros. Detalles en la [política de cookies](/politica-de-cookies/).

## Terceros

Google puede usar cookies para mostrar anuncios basados en visitas previas. Puedes gestionar la personalización en la configuración de anuncios de Google.

## Tus derechos

Puedes solicitar acceso, rectificación o eliminación de los datos que nos hayas enviado por correo, escribiendo a través de [contacto](/contacto/).

## Seguridad

Aplicamos medidas razonables para proteger la información, aunque ningún sistema es infalible.

## Cambios

Podemos actualizar esta política. La fecha de revisión aparece en la parte superior.
<!-- PAGE:END -->

<!-- PAGE:START slug=politica-de-cookies -->
---
title: "Política de cookies | Matriculación Vehicular"
description: "Qué cookies usa matriculacionvehicular.com, para qué sirven y cómo desactivarlas."
h1: "Política de cookies"
short: "Cookies"
type: confianza
schema: WebPage
updated: 2026-10-27
show_date: true
related: [politica-de-privacidad, aviso-legal, contacto]
---
## Qué son

Las cookies son pequeños archivos que se guardan en tu navegador para recordar información.

## Cookies que usamos

| Tipo | Proveedor | Finalidad |
|---|---|---|
| Analítica | Google Analytics | Medir visitas y uso del sitio |
| Publicidad | Google AdSense | Mostrar anuncios |
| Técnicas | Este sitio | Funcionamiento básico |

## Cómo desactivarlas

Puedes bloquearlas o borrarlas desde la configuración de tu navegador. Si las desactivas, algunas funciones pueden verse afectadas. También puedes gestionar la personalización de anuncios en la configuración de anuncios de Google.

## Más información

Consulta la [política de privacidad](/politica-de-privacidad/).
<!-- PAGE:END -->

<!-- PAGE:START slug=aviso-legal -->
---
title: "Aviso legal | Matriculación Vehicular Ecuador"
description: "Aviso legal de matriculacionvehicular.com: sitio informativo no oficial, límites de responsabilidad y propiedad del contenido."
h1: "Aviso legal"
short: "Aviso legal"
type: confianza
schema: WebPage
updated: 2026-10-27
show_date: true
related: [sobre-nosotros, politica-de-privacidad, contacto]
---
## Sitio informativo no oficial

matriculacionvehicular.com es un sitio **informativo e independiente**. No pertenece ni representa al Gobierno del Ecuador, a la ANT, al SRI, a la SPPAT ni a ningún municipio.

## Alcance de la información

La información se ofrece con fines orientativos. Las normas, tarifas y plazos cambian; verifica siempre en los [portales oficiales](/fuentes-oficiales-ecuador/) antes de tomar decisiones o realizar pagos.

## Limitación de responsabilidad

No nos responsabilizamos por decisiones tomadas con base en el contenido ni por daños derivados del uso del sitio o de sitios enlazados.

## Enlaces externos

Los enlaces a terceros son referencias; no controlamos su contenido.

## Propiedad intelectual

Los textos y diseño del sitio pertenecen a su editor. Puedes citar fragmentos breves indicando la fuente.

## Contacto

Para cualquier consulta, usa [contacto](/contacto/).
<!-- PAGE:END -->

<!-- PAGE:START slug=404 -->
---
title: "Página no encontrada | Matriculación Vehicular"
description: "La página que buscas no existe. Encuentra tu trámite desde el índice de matriculación vehicular."
h1: "No encontramos esa página"
short: "404"
type: confianza
schema: WebPage
updated: 2026-10-27
related: [tramites-vehiculares, calendario-matriculacion-vehicular, valor-a-pagar-matricula]
---
La dirección que buscas no existe o fue reemplazada. Prueba con estos atajos:

- [Calendario de matriculación](/calendario-matriculacion-vehicular/)
- [Valor a pagar](/valor-a-pagar-matricula/)
- [Todos los trámites](/tramites-vehiculares/)
- [Portales oficiales](/fuentes-oficiales-ecuador/)
<!-- PAGE:END -->

## 10. Datos que deben verificarse antes de publicar

| Página | Dato a confirmar |
|---|---|
| `calendario-matriculacion-vehicular` | Calendario 2026 por dígito: confirmar contra la resolución vigente de la ANT y las variantes de AMT, ATM y EMOV EP. |
| `calendario-matriculacion-vehicular` | Estado de plazos y posible ampliación de diciembre: confirmar en el portal oficial antes de publicar. |
| `valor-a-pagar-matricula` | Tabla progresiva del impuesto a la propiedad por avalúo: confirmar rangos y valores vigentes con el SRI. |
| `valor-a-pagar-matricula` | Valor del SPPAT por clase de vehículo: confirmar tarifa vigente. |
| `valor-a-pagar-matricula` | Valor de tasas de matriculación ANT/GAD y de RTV por ciudad: confirmar. |
| `multas-por-no-matricular-vehiculo` | Monto de la multa por no matricular y por circular sin placas (porcentaje del SBU 2026): confirmar en normativa vigente (COIP y resoluciones). |
| `multas-por-no-matricular-vehiculo` | Recargos por mora en matrícula: confirmar mecánica de cálculo con ANT/SRI. |
| `revision-tecnica-vehicular` | Tarifas RTV Quito 2026 tomadas de Primicias (fuente AMT); el portal de la AMT bloquea lecturas automáticas. |
| `revision-tecnica-vehicular` | Plazos de segunda revisión por ciudad: confirmar. |
| `cambio-de-propietario-vehicular` | Costo del traspaso: 1% (SRI), valores de la tasa ANT y especie USD 22, plazo de 30 días y multa 5% SBU: confirmar con normativa vigente. |
| `cambio-de-caracteristicas-del-vehiculo` | Requisitos y costos exactos por tipo de cambio (color, motor, carrocería): confirmar con la entidad de tránsito de cada ciudad. |
| `matriculacion-de-vehiculos-nuevos` | Duración de la exoneración de RTV para vehículos nuevos por ciudad: confirmar. |
| `matriculacion-de-vehiculos-nuevos` | Documentos exactos del concesionario/importador y tasa de placas: confirmar. |
| `matriculacion-vehicular-quito` | Valores de la tabla RTV 2026 provienen de Primicias (fuente AMT, ene 2026); el portal de la AMT bloquea lecturas automáticas y no se pudo contrastar directamente. |
| `matriculacion-vehicular-quito` | Horarios de centros: la ficha municipal indica lun-vie 08:00-17:00 y sáb 08:00-12:00; la prensa de enero 2026 indicó otros horarios para el esquema con turno. Confirmar en la AMT. |
| `matriculacion-vehicular-guayaquil` | Tarifario 2026 tomado del memorando del 19 de enero de 2026; confirmar que no haya una reforma posterior. |
| `matriculacion-vehicular-guayaquil` | Prórrogas sin multa por dígito (4 hasta el 6 de junio; 1 hasta el 14 de marzo) son avisos puntuales de 2026, no reglas permanentes. |
| `matriculacion-vehicular-cuenca` | Tarifa de la revisión técnica en Cuenca: no se encontró el valor vigente en la fuente oficial. Confirmar con EMOV EP antes de publicar una cifra. |
| `matriculacion-vehicular-cuenca` | Costo del CUV en Cuenca (USD 10) proviene del documento de requisitos de la EMOV; el tarifario nacional de la ANT también indica USD 10. |
| `matriculacion-vehicular-ambato` | Entidad que atiende hoy a los vehículos de Ambato (GAD municipal o Mancomunidad): confirmar antes de publicar como regla. |
| `matriculacion-vehicular-ambato` | Tarifa de revisión técnica en Ambato: una publicación de 2026 muestra valores iguales a los de Quito; no se encontró fuente oficial. No publicada. |
| `matriculacion-vehicular-ambato` | Teléfono (03) 2997800 ext. 3332 y exoneración de modelos 2021 o posteriores provienen de un aviso de 2023; pueden estar desactualizados. |
| `matriculacion-vehicular-riobamba` | Tarifa de revisión técnica en Riobamba: no se encontró fuente oficial. No publicada. |
| `matriculacion-vehicular-riobamba` | Los requisitos se publican como imágenes en el portal municipal; confirmar cada trámite directamente. |
| `revision-tecnica-vehicular-quito` | Tarifas tomadas de Primicias (fuente AMT, enero 2026). La ficha municipal indica el valor como variable sin cifras; contrastar con el portal de la AMT. |
| `revision-tecnica-vehicular-guayaquil` | Tarifario del memorando EPMTMG-DFI-2026-0143-M (19 ene 2026); confirmar vigencia. |
| `revision-tecnica-vehicular-cuenca` | Tarifa de la revisión en Cuenca: no se encontró cifra oficial vigente. Confirmar con EMOV EP. No se publica el valor de USD 20 usado antes. |
| `certificado-unico-vehicular` | Costo del CUV (referencia USD 7,50 a 10) y canal de emisión actual: confirmar. |
| `matricula-moto` | Valores de SPPAT y tasas para motocicletas: confirmar tarifas vigentes. |
| `sppat` | Coberturas, montos asegurados y tarifa por clase de vehículo: confirmar con SPPAT. |
| `vehiculos-electricos-exoneracion-matricula` | Alcance exacto de la exoneración EV (IPVM y SPPAT) y vigencia: confirmar con SRI/SPPAT y la normativa de 2026. |
| `rebaja-matricula-adultos-mayores-discapacidad` | Porcentajes de rebaja, límite de avalúo, número de vehículos y requisitos de acreditación: confirmar con SRI y normativa vigente. |
| `bloqueo-vehicular-desbloqueo` | Procedimiento de levantamiento por tipo de bloqueo y tasas: confirmar con la entidad que lo dispuso. |
| `turno-matriculacion-vehicular` | Canal y condiciones de agendamiento por ciudad: confirmar en cada entidad. |
| `duplicado-de-placas-vehiculares` | Costos de duplicado de placas (USD 23/13) y especie (USD 22), sanción por circular sin placas (30% SBU): confirmar. |
| `matriculacion-de-vehiculos-importados` | Requisitos aduaneros vigentes (aranceles, restricciones por antigüedad, homologación): confirmar con SENAE y normativa de 2026. |
| `permiso-de-circulacion-temporal` | Duración, costo y ámbito del permiso temporal vigente: confirmar con la entidad. |
| `exoneracion-de-impuestos-vehiculares` | Lista actual de exoneraciones, porcentajes y requisitos: confirmar con SRI. |
| `cambio-de-servicio-vehicular` | Requisitos y costo del cambio de servicio por entidad: confirmar. |
| `duplicado-de-matricula-vehicular` | Tasa del duplicado de matrícula y canal digital vigente: confirmar. |
| `baja-vehiculo` | Causales de baja, requisitos y tasas vigentes: confirmar. |
| `pago-matricula-linea` | Canales de pago activos y entidades financieras autorizadas por ciudad: confirmar. |
| `consulta-multas-transito` | Portales de consulta vigentes por ciudad y datos requeridos: confirmar. |
| `contacto` | Crear la cuenta de correo publicada (contacto@matriculacionvehicular.com) antes del lanzamiento o sustituirla por la real. |

Orden sugerido: (1) calendario y variantes por ciudad, (2) tarifas de revisión técnica de Quito, Guayaquil y Cuenca, (3) montos de multas y plazos de traspaso, (4) tablas del impuesto y del SPPAT, (5) datos locales de Ambato y Riobamba.

## 11. Mapa de redirecciones 301 / 410 de los 180 posts antiguos

Formato: `URL antigua, código, destino`. **172 redirigen con 301** a la página pilar correspondiente y **8 devuelven 410** por duplicado o falta de valor. El build valida que cada destino exista y que ninguna URL antigua choque con una página viva. Las reglas de asignación están en la propia tabla; para añadir más posts, agrega líneas dentro del bloque.

<!-- REDIRECTS:START -->
/que-documentos-necesitas-para-solicitar-el-certificado-de-matricula/, 301, /certificado-unico-vehicular/
/beneficios-de-tener-el-certificado-de-matriculacion-vehicular-al-dia/, 301, /certificado-unico-vehicular/
/diferencias-entre-el-certificado-de-matriculacion-original-y-duplicado/, 301, /certificado-unico-vehicular/
/cuanto-tiempo-es-valido-el-certificado-de-matriculacion-en-ecuador/, 301, /certificado-unico-vehicular/
/consejos-para-mantener-al-dia-el-certificado-de-matriculacion-vehicular/, 301, /certificado-unico-vehicular/
/cuanto-cuesta-obtener-un-certificado-de-matriculacion-en-ecuador/, 301, /certificado-unico-vehicular/
/que-hacer-si-pierdes-el-certificado-de-matricula-de-tu-vehiculo/, 301, /certificado-unico-vehicular/
/requisitos-para-tramitar-el-certificado-de-matriculacion-vehicular/, 301, /certificado-unico-vehicular/
/pasos-para-obtener-el-certificado-de-matricula-de-tu-vehiculo/, 301, /certificado-unico-vehicular/
/como-solicitar-el-certificado-de-matriculacion-vehicular-en-ecuador/, 301, /certificado-unico-vehicular/
/donde-y-como-solicitar-la-reposicion-de-placas-en-ecuador/, 301, /duplicado-de-placas-vehiculares/
/que-hacer-si-las-placas-que-recibes-tienen-errores-o-defectos/, 301, /duplicado-de-placas-vehiculares/
/cuanto-tiempo-tarda-en-llegar-la-reposicion-de-placas-vehiculares/, 301, /duplicado-de-placas-vehiculares/
/cuales-son-las-sanciones-por-circular-sin-placas-en-ecuador/, 301, /multas-por-no-matricular-vehiculo/
/que-hacer-si-tus-placas-vehiculares-estan-danadas-o-ilegibles/, 301, /duplicado-de-placas-vehiculares/
/consejos-para-evitar-la-perdida-o-robo-de-placas-vehiculares/, 301, /duplicado-de-placas-vehiculares/
/costos-y-plazos-para-la-reposicion-de-placas-en-ecuador/, 301, /duplicado-de-placas-vehiculares/
/requisitos-para-obtener-nuevas-placas-vehiculares-en-ecuador/, 301, /duplicado-de-placas-vehiculares/
/pasos-a-seguir-si-pierdes-o-te-roban-las-placas-de-tu-vehiculo/, 301, /duplicado-de-placas-vehiculares/
/cuanto-tiempo-toma-el-proceso-de-baja-vehicular-en-ecuador/, 301, /baja-vehiculo/
/como-solicitar-la-reposicion-de-placas-vehiculares-en-ecuador/, 301, /duplicado-de-placas-vehiculares/
/que-vehiculos-pueden-ser-dados-de-baja-en-ecuador/, 301, /baja-vehiculo/
/que-sanciones-existen-si-no-das-de-baja-un-vehiculo-inoperante/, 301, /bloqueo-vehicular-desbloqueo/
/consejos-para-dar-de-baja-tu-vehiculo-de-forma-rapida-y-sencilla/, 301, /baja-vehiculo/
/beneficios-de-dar-de-baja-un-vehiculo-que-no-usas-en-ecuador/, 301, /baja-vehiculo/
/que-hacer-si-quieres-dar-de-baja-un-vehiculo-por-siniestro-o-destruccion/, 301, /baja-vehiculo/
/cuanto-cuesta-dar-de-baja-un-vehiculo-en-ecuador/, 301, /baja-vehiculo/
/requisitos-y-documentos-para-dar-de-baja-un-vehiculo-en-ecuador/, 301, /baja-vehiculo/
/pasos-a-seguir-para-dar-de-baja-un-vehiculo-que-ya-no-usas/, 301, /baja-vehiculo/
/como-dar-de-baja-un-vehiculo-en-ecuador-guia-completa/, 301, /baja-vehiculo/
/beneficios-de-actualizar-correctamente-el-servicio-de-tu-vehiculo/, 301, /cambio-de-servicio-vehicular/
/cuales-son-las-sanciones-por-no-realizar-el-cambio-de-servicio-vehicular/, 301, /cambio-de-servicio-vehicular/
/diferencias-entre-un-vehiculo-de-servicio-particular-y-uno-comercial-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/consejos-para-agilizar-el-tramite-de-cambio-de-servicio-vehicular-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/que-sucede-si-no-se-actualiza-el-servicio-de-un-vehiculo-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/que-documentos-necesitas-para-cambiar-el-servicio-de-tu-vehiculo/, 301, /cambio-de-servicio-vehicular/
/cuanto-cuesta-cambiar-el-servicio-de-un-vehiculo-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/pasos-para-cambiar-el-uso-de-tu-vehiculo-de-particular-a-publico/, 301, /cambio-de-servicio-vehicular/
/requisitos-para-realizar-el-cambio-de-servicio-vehicular-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/como-cambiar-el-servicio-de-un-vehiculo-de-particular-a-comercial-en-ecuador/, 301, /cambio-de-servicio-vehicular/
/consejos-para-evitar-problemas-al-matricular-vehiculos-importados-en-ecuador/, 301, /matriculacion-de-vehiculos-importados/
/que-sanciones-existen-por-no-matricular-un-vehiculo-importado-a-tiempo/, 301, /matriculacion-de-vehiculos-importados/
/que-vehiculos-importados-deben-cumplir-con-normas-de-matriculacion-especiales/, 301, /matriculacion-de-vehiculos-importados/
/cuales-son-los-plazos-para-matricular-un-vehiculo-importado-en-ecuador/, 301, /matriculacion-de-vehiculos-importados/
/pasos-para-regularizar-la-matricula-de-un-vehiculo-importado/, 301, /matriculacion-de-vehiculos-importados/
/que-hacer-si-tu-vehiculo-importado-no-pasa-la-revision-tecnica-en-ecuador/, 301, /matriculacion-de-vehiculos-importados/
/documentos-necesarios-para-matricular-un-vehiculo-importado/, 301, /matriculacion-de-vehiculos-importados/
/requisitos-para-la-matriculacion-de-vehiculos-importados-en-ecuador/, 301, /matriculacion-de-vehiculos-importados/
/cuanto-cuesta-matricular-un-vehiculo-importado-en-ecuador/, 301, /matriculacion-de-vehiculos-importados/
/como-matricular-un-vehiculo-importado-en-ecuador-guia-paso-a-paso/, 301, /matriculacion-de-vehiculos-importados/
/cuanto-tiempo-tienes-para-matricular-un-vehiculo-nuevo-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/que-impuestos-y-tasas-debes-pagar-al-matricular-un-vehiculo-nuevo/, 301, /matriculacion-de-vehiculos-nuevos/
/consejos-para-agilizar-la-matriculacion-de-un-vehiculo-nuevo-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/beneficios-de-matricular-un-vehiculo-nuevo-en-ecuador-a-tiempo/, 301, /matriculacion-de-vehiculos-nuevos/
/que-hacer-si-no-puedes-matricular-tu-vehiculo-nuevo-de-inmediato/, 301, /matriculacion-de-vehiculos-nuevos/
/documentos-necesarios-para-matricular-un-auto-nuevo-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/requisitos-para-la-matriculacion-de-vehiculos-nuevos-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/cuanto-cuesta-matricular-un-vehiculo-nuevo-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/pasos-para-matricular-un-auto-recien-comprado-en-ecuador/, 301, /matriculacion-de-vehiculos-nuevos/
/cuanto-tiempo-es-valido-el-permiso-de-circulacion-temporal-en-ecuador/, 301, /permiso-de-circulacion-temporal/
/como-matricular-un-vehiculo-nuevo-en-ecuador-guia-completa/, 301, /matriculacion-de-vehiculos-nuevos/
/diferencias-entre-el-permiso-de-circulacion-temporal-y-la-matriculacion-definitiva/, 301, /permiso-de-circulacion-temporal/
/que-sucede-si-no-tienes-un-permiso-de-circulacion-temporal-en-regla/, 301, /permiso-de-circulacion-temporal/
/consejos-para-usar-el-permiso-de-circulacion-temporal-sin-problemas/, 301, /permiso-de-circulacion-temporal/
/pasos-para-obtener-un-permiso-de-circulacion-temporal-de-forma-rapida/, 301, /permiso-de-circulacion-temporal/
/costos-y-plazos-para-obtener-un-permiso-de-circulacion-temporal/, 301, /permiso-de-circulacion-temporal/
/que-vehiculos-requieren-un-permiso-de-circulacion-temporal-en-ecuador/, 301, /permiso-de-circulacion-temporal/
/cuando-necesitas-un-permiso-de-circulacion-temporal-para-tu-vehiculo/, 301, /permiso-de-circulacion-temporal/
/como-solicitar-un-permiso-de-circulacion-temporal-para-tu-vehiculo-en-ecuador/, 301, /permiso-de-circulacion-temporal/
/requisitos-para-obtener-el-permiso-de-circulacion-temporal-en-ecuador/, 301, /permiso-de-circulacion-temporal/
/cuales-son-las-ventajas-de-la-exoneracion-de-impuestos-en-ecuador/, 301, /exoneracion-de-impuestos-vehiculares/
/guia-de-exoneracion-de-impuestos-vehiculares-quienes-pueden-solicitarla/, 301, /exoneracion-de-impuestos-vehiculares/
/que-hacer-si-no-calificas-para-la-exoneracion-de-impuestos-vehiculares/, 301, /exoneracion-de-impuestos-vehiculares/
/que-impuestos-vehiculares-pueden-ser-exonerados-en-ecuador/, 301, /exoneracion-de-impuestos-vehiculares/
/pasos-para-solicitar-la-exoneracion-de-impuestos-vehiculares-en-ecuador/, 301, /exoneracion-de-impuestos-vehiculares/
/cuanto-tiempo-dura-la-exoneracion-de-impuestos-para-vehiculos-electricos/, 301, /vehiculos-electricos-exoneracion-matricula/
/beneficios-de-la-exoneracion-de-impuestos-para-vehiculos-ecologicos/, 301, /vehiculos-electricos-exoneracion-matricula/
/requisitos-para-la-exoneracion-de-impuestos-en-vehiculos-electricos-en-ecuador/, 301, /vehiculos-electricos-exoneracion-matricula/
/que-vehiculos-son-elegibles-para-la-exoneracion-de-impuestos-vehiculares/, 301, /exoneracion-de-impuestos-vehiculares/
/como-obtener-la-exoneracion-de-impuestos-vehiculares-en-ecuador/, 301, /exoneracion-de-impuestos-vehiculares/
/cuanto-tiempo-tarda-el-tramite-de-cambio-de-caracteristicas-vehiculares/, 301, /cambio-de-caracteristicas-del-vehiculo/
/que-hacer-si-realizas-modificaciones-no-autorizadas-a-tu-vehiculo/, 301, /cambio-de-caracteristicas-del-vehiculo/
/cambios-de-caracteristicas-vehiculares-lo-que-debes-saber-antes-de-hacerlo/, 301, /cambio-de-caracteristicas-del-vehiculo/
/como-modificar-las-caracteristicas-tecnicas-de-un-vehiculo-en-ecuador/, 301, /cambio-de-caracteristicas-del-vehiculo/
/costos-y-pasos-para-cambiar-las-caracteristicas-de-un-vehiculo-en-ecuador/, 301, /cambio-de-caracteristicas-del-vehiculo/
/cuales-son-las-sanciones-por-no-reportar-cambios-en-las-caracteristicas-del-vehiculo/, 301, /cambio-de-caracteristicas-del-vehiculo/
/requisitos-para-cambiar-el-color-motor-o-carroceria-de-un-vehiculo-en-ecuador/, 301, /cambio-de-caracteristicas-del-vehiculo/
/que-cambios-en-las-caracteristicas-del-vehiculo-requieren-actualizacion-de-matricula/, 301, /cambio-de-caracteristicas-del-vehiculo/
/tramites-para-actualizar-las-caracteristicas-de-tu-vehiculo-en-la-matricula/, 301, /cambio-de-caracteristicas-del-vehiculo/
/como-realizar-el-cambio-de-caracteristicas-vehiculares-en-ecuador/, 301, /cambio-de-caracteristicas-del-vehiculo/
/consejos-para-proteger-tu-matricula-vehicular-y-evitar-su-perdida/, 301, /duplicado-de-matricula-vehicular/
/donde-y-como-solicitar-un-duplicado-de-matricula-vehicular-en-ecuador/, 301, /duplicado-de-matricula-vehicular/
/beneficios-de-tener-tu-matricula-vehicular-en-buen-estado/, 301, /duplicado-de-matricula-vehicular/
/cuales-son-los-motivos-para-solicitar-un-duplicado-de-matricula/, 301, /duplicado-de-matricula-vehicular/
/costos-del-duplicado-de-matricula-vehicular-en-ecuador/, 301, /duplicado-de-matricula-vehicular/
/como-obtener-un-duplicado-de-matricula-vehicular-de-forma-rapida/, 301, /duplicado-de-matricula-vehicular/
/requisitos-para-obtener-un-duplicado-de-la-matricula-vehicular/, 301, /duplicado-de-matricula-vehicular/
/pasos-a-seguir-si-pierdes-la-matricula-de-tu-vehiculo-en-ecuador/, 301, /duplicado-de-matricula-vehicular/
/que-hacer-si-tu-matricula-vehicular-se-dana-o-deteriora/, 301, /duplicado-de-matricula-vehicular/
/como-solicitar-un-duplicado-de-matricula-vehicular-en-ecuador/, 301, /duplicado-de-matricula-vehicular/
/cambio-de-propietario-vehicular-lo-que-debes-saber-antes-de-vender-tu-auto/, 301, /cambio-de-propietario-vehicular/
/cuanto-tiempo-tienes-para-hacer-el-cambio-de-propietario-de-un-vehiculo/, 301, /cambio-de-propietario-vehicular/
/consejos-para-evitar-problemas-al-transferir-la-propiedad-de-un-vehiculo/, 301, /cambio-de-propietario-vehicular/
/guia-de-pasos-para-transferir-un-vehiculo-a-un-nuevo-dueno-en-ecuador/, 301, /cambio-de-propietario-vehicular/
/multas-y-sanciones-por-no-realizar-el-cambio-de-propietario-vehicular/, 301, /cambio-de-propietario-vehicular/
/que-sucede-si-no-se-registra-el-cambio-de-propietario-de-un-vehiculo/, 301, /cambio-de-propietario-vehicular/
/documentos-requeridos-para-el-cambio-de-propietario-vehicular-en-ecuador/, 301, /cambio-de-propietario-vehicular/
/costos-y-pasos-para-realizar-el-cambio-de-propietario-vehicular-en-ecuador/, 301, /cambio-de-propietario-vehicular/
/como-transferir-la-propiedad-de-un-vehiculo-en-ecuador-guia-completa/, 301, /cambio-de-propietario-vehicular/
/beneficios-de-pagar-tus-impuestos-vehiculares-de-manera-anticipada/, 301, /valor-a-pagar-matricula/
/todo-lo-que-necesitas-para-realizar-el-cambio-de-propietario-vehicular-en-ecuador/, 301, /cambio-de-propietario-vehicular/
/como-calcular-el-monto-de-los-impuestos-vehiculares-en-ecuador/, 301, /valor-a-pagar-matricula/
/alternativas-de-pago-para-impuestos-vehiculares-en-ecuador/, 301, /pago-matricula-linea/
/consejos-para-evitar-sanciones-por-falta-de-pago-de-impuestos-vehiculares/, 301, /multas-por-no-matricular-vehiculo/
/que-hacer-si-tienes-multas-por-impuestos-vehiculares-atrasados/, 301, /multas-por-no-matricular-vehiculo/
/cuales-son-las-tasas-e-impuestos-vehiculares-en-ecuador/, 301, /valor-a-pagar-matricula/
/guia-para-el-pago-de-impuestos-vehiculares-en-ecuador-paso-a-paso/, 301, /pago-matricula-linea/
/multas-por-no-pagar-los-impuestos-vehiculares-a-tiempo-en-ecuador/, 301, /multas-por-no-matricular-vehiculo/
/que-impuestos-vehiculares-debes-pagar-en-ecuador-en-2024/, 301, /valor-a-pagar-matricula/
/como-realizar-el-pago-de-impuestos-vehiculares-en-ecuador-en-linea/, 301, /pago-matricula-linea/
/que-hacer-si-no-realizas-la-matriculacion-anual-de-tu-vehiculo-a-tiempo/, 301, /multas-por-no-matricular-vehiculo/
/costos-de-la-matriculacion-vehicular-anual-en-ecuador-lo-que-debes-saber/, 301, /valor-a-pagar-matricula/
/beneficios-de-mantener-tu-vehiculo-con-la-matriculacion-al-dia-en-ecuador/, 301, /matriculacion-anual-vehicular/
/que-documentos-necesitas-para-matricular-tu-vehiculo-cada-ano/, 301, /matriculacion-anual-vehicular/
/errores-comunes-al-matricular-tu-vehiculo-en-ecuador-y-como-evitarlos/, 301, /matriculacion-anual-vehicular/
/consejos-para-agilizar-tu-proceso-de-matriculacion-anual-en-ecuador/, 301, /matriculacion-anual-vehicular/
/calendario-de-matriculacion-anual-vehicular-en-ecuador-fechas-y-plazos/, 301, /calendario-matriculacion-vehicular/
/guia-paso-a-paso-para-la-matriculacion-anual-de-vehiculos-en-ecuador/, 301, /matriculacion-anual-vehicular/
/requisitos-para-la-matriculacion-vehicular-en-ecuador-en-2024/, 301, /matriculacion-anual-vehicular/
/que-es-la-matriculacion-anual-vehicular-y-como-realizarla-en-ecuador/, 301, /matriculacion-anual-vehicular/
/pasos-clave-para-renovar-tu-matricula-vehicular-facilmente/, 301, /matriculacion-anual-vehicular/
/pasos-esenciales-para-una-correcta-matriculacion-vehicular/, 301, /matriculacion-anual-vehicular/
/documentacion-requerida-para-matricula-nacional-vs-provincial-guia-esencial/, 301, /tramites-vehiculares/
/logre-evitar-multas-con-este-metodo-eficaz/, 410,
/tipos-de-vehiculos-y-sus-requisitos-especificos-en-ecuador/, 301, /tramites-vehiculares/
/como-elegir-el-mejor-lugar-para-realizar-la-matricula/, 301, /matriculacion-por-ciudad/
/tipos-de-multas-por-matricula-vehicular-no-realizada/, 301, /multas-por-no-matricular-vehiculo/
/pago-unico-vs-cuotas-para-vehiculos-que-conviene-mas/, 301, /valor-a-pagar-matricula/
/matriculacion-en-linea-vs-presencial-cual-elegir/, 301, /pago-matricula-linea/
/consecuencias-legales-por-no-registrar-vehiculos/, 301, /multas-por-no-matricular-vehiculo/
/que-hace-obligatorio-el-tramite-vehicular-en-ecuador/, 410,
/como-evitar-errores-comunes-al-matricular-un-auto-en-ecuador/, 301, /matriculacion-anual-vehicular/
/matricula-vehicular-como-agilizar-tu-tramite-facilmente/, 301, /matriculacion-anual-vehicular/
/consejos-esenciales-para-evitar-errores-comunes-al-matricular/, 301, /matriculacion-anual-vehicular/
/registro-tradicional-frente-a-digitalizado-ventajas-y-desventajas/, 301, /pago-matricula-linea/
/matricula-vehicular-como-dominarlo-en-poco-tiempo/, 301, /matriculacion-anual-vehicular/
/guia-completa-de-matricula-vehicular-en-ecuador/, 301, /matriculacion-anual-vehicular/
/primeros-pasos-para-matricular-tu-vehiculo-exitosamente/, 301, /matriculacion-anual-vehicular/
/errores-comunes-al-registrar-un-auto-en-ecuador/, 301, /matriculacion-anual-vehicular/
/que-documentos-necesito-para-matricular-un-vehiculo/, 301, /matriculacion-anual-vehicular/
/que-riesgos-enfrentas-al-matricular-tarde-tu-vehiculo/, 301, /multas-por-no-matricular-vehiculo/
/cuales-son-los-costos-ocultos-al-registrar-tu-auto/, 301, /valor-a-pagar-matricula/
/por-que-es-crucial-matricular-tu-vehiculo/, 410,
/tips-indispensables-para-una-matriculacion-sin-complicaciones/, 301, /matriculacion-anual-vehicular/
/importacion-de-autos-usados-vs-nuevos-que-conviene-mas/, 301, /matriculacion-de-vehiculos-importados/
/por-que-es-crucial-conocer-requisitos-para-matricula/, 410,
/guia-definitiva-para-el-tramite-de-matricula-vehicular/, 301, /matriculacion-anual-vehicular/
/metodos-efectivos-para-acelerar-la-matricula-vehicular/, 301, /matriculacion-anual-vehicular/
/matricula-de-vehiculos-en-ecuador-como-dominarlo-en-poco-tiempo/, 301, /matriculacion-anual-vehicular/
/consejos-esenciales-para-registrar-tu-vehiculo-correctamente/, 301, /matriculacion-anual-vehicular/
/plazos-de-matricula-versus-sanciones-por-demora-mejor-opcion/, 301, /multas-por-no-matricular-vehiculo/
/consecuencias-legales-del-incumplimiento-en-la-matriculacion/, 301, /multas-por-no-matricular-vehiculo/
/pasos-clave-que-debes-seguir-al-matricular-tu-vehiculo/, 301, /matriculacion-anual-vehicular/
/que-hacer-si-no-recibiste-la-matricula-a-tiempo/, 301, /duplicado-de-matricula-vehicular/
/como-evitar-errores-comunes-al-matricular-tu-vehiculo/, 301, /matriculacion-anual-vehicular/
/ahorro-en-impuestos-vehiculares-o-matriculacion-regular-comparativa-clave/, 301, /valor-a-pagar-matricula/
/que-documentos-necesitas-para-el-tramite-de-matricula/, 301, /matriculacion-anual-vehicular/
/tips-esenciales-para-realizar-tu-matricula-sin-problemas/, 301, /matriculacion-anual-vehicular/
/guia-completa-sobre-matriculacion-vehicular-en-ecuador-todo-lo-que-necesitas-saber/, 301, /matriculacion-anual-vehicular/
/guia-para-principiantes-sobre-la-matriculacion-vehicular-simplificada/, 301, /matriculacion-anual-vehicular/
/evaluacion-del-registro-de-vehiculos-para-nuevos-propietarios/, 301, /matriculacion-anual-vehicular/
/estudio-de-caso-transformacion-del-proceso-de-matricula-en-guayaquil/, 410,
/revision-tecnica-vehicular-o-matriculacion-analisis-exhaustivo/, 301, /revision-tecnica-vehicular/
/como-registre-mi-auto-en-quito-rapidamente/, 301, /matriculacion-vehicular-quito/
/matriculacion-en-linea-vs-presencial-cual-elegir-2/, 410,
/registro-de-vehiculos-ecologicos-o-tradicionales-analisis-completo/, 301, /vehiculos-electricos-exoneracion-matricula/
/importancia-del-registro-vehicular-para-la-seguridad-ciudadana/, 410,
/guia-para-principiantes-matriculacion-vehicular-simplificada-para-nuevos-propietarios/, 301, /matriculacion-anual-vehicular/
/matriculacion-vehicular-mi-sincera-opinion-personal/, 410,
/beneficios-de-mantener-tu-matricula-al-dia/, 301, /matriculacion-anual-vehicular/
<!-- REDIRECTS:END -->

## 12. Lista de comprobación de lanzamiento

**Antes del cambio de DNS**
- [ ] `python build.py … --strict` sin errores; revisar `build-report.md`.
- [ ] Todos los datos de la sección 10 confirmados o marcados como referencia.
- [ ] Logo, favicon y `og-default.jpg` colocados; fuentes Poppins presentes.
- [ ] Probar en móvil (menú, selector de dígito, tablas con desplazamiento).
- [ ] Revisar que no haya texto de España (`DGT`, `ITV`, «coche»).
- [ ] Verificar `view-source` de una página: un único `<h1>`, canonical correcta, JSON-LD válido (Prueba de resultados enriquecidos), solo el script de AdSense (sin `<ins>`).
- [ ] Crear el correo `contacto@…` o sustituirlo.
- [ ] Repositorio de GitHub en **privado**.

**Día del lanzamiento**
- [ ] Cambiar DNS y activar HTTPS; confirmar `www` → raíz.
- [ ] Probar 10 URL antiguas con 301 (por ejemplo, las de mayor tráfico) y 2 de las 410.
- [ ] Enviar `sitemap.xml` en Search Console y en Bing; ejecutar IndexNow.
- [ ] Confirmar `ads.txt` en `/ads.txt` y estado del sitio en AdSense.

**Primeras 4 semanas**
- [ ] Revisar cobertura e impresiones por país (no debe volver a dominar España).
- [ ] Ver el CLS y la carga de anuncios; subir la densidad con cuidado.
- [ ] Ampliar las páginas locales con datos oficiales verificados.
- [ ] Registrar cada cambio de normas o tarifas en `/blog/` con fecha y fuente.
