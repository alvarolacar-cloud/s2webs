from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = Path(r"C:\Users\alvaro\Desktop\S2Webs\contenido-paginas.md")


PAGE_ORDER = [
    "services",
    "web-design",
    "affordable-seo",
    "ecommerce-website-design",
    "lightning-platform",
    "website-health-check",
    "portfolio",
    "portfolio-search",
    "case-studies",
    "why-it-seeze",
    "uk-support-network",
    "careers",
    "compare",
    "prices",
    "spark-package",
    "lightning-package",
    "shop-package",
    "blog",
    "contact",
    "quick-quote",
    "faqs",
]

PAGE_TITLES = {
    "services": "Servicios",
    "web-design": "Diseño web",
    "affordable-seo": "SEO asequible",
    "ecommerce-website-design": "Ecommerce",
    "lightning-platform": "Agentic",
    "website-health-check": "Revisión web",
    "portfolio": "Portfolio",
    "portfolio-search": "Buscar portfolio",
    "case-studies": "Casos de éxito",
    "why-it-seeze": "Por qué S2Webs",
    "uk-support-network": "Soporte",
    "careers": "Trabaja con nosotros",
    "compare": "Comparativa",
    "prices": "Precios",
    "spark-package": "Paquete Inicial",
    "lightning-package": "Paquete Agentic",
    "shop-package": "Paquete Tienda",
    "blog": "Blog",
    "contact": "Contacto",
    "quick-quote": "Presupuesto",
    "faqs": "Preguntas frecuentes",
}


def slug_to_file(slug: str) -> str:
    return "index.html" if slug == "home" else f"{slug}.html"


def parse_markdown(text: str) -> dict[str, list[str]]:
    pages: dict[str, list[str]] = {}
    current_slug: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        match = re.match(r"^## ([a-z0-9-]+)\.png\s*$", line)
        if match:
            if current_slug:
                pages[current_slug] = current_lines
            current_slug = match.group(1)
            current_lines = []
            continue
        if current_slug:
            if line.startswith("# ") or line.startswith("Las siguientes páginas"):
                continue
            current_lines.append(line)

    if current_slug:
        pages[current_slug] = current_lines
    return pages


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    title = "Contenido"
    buf: list[str] = []
    for line in lines:
        if line.startswith("### "):
            if buf or title != "Contenido":
                sections.append((title, buf))
            title = line[4:].strip()
            buf = []
        elif line.startswith("---"):
            continue
        else:
            buf.append(line)
    if buf or title != "Contenido":
        sections.append((title, buf))
    return sections


def first_value(lines: list[str], keys: tuple[str, ...]) -> str | None:
    for line in lines:
        for key in keys:
            if line.startswith(key):
                return line.split(":", 1)[1].strip()
    return None


def paragraph(text: str) -> str:
    return f"<p>{html.escape(text)}</p>"


def action_href(text: str) -> str:
    lower = text.lower()
    if "portfolio" in lower or "proyecto" in lower:
        return "portfolio.html"
    if "precio" in lower or "presupuesto" in lower or "primer paso" in lower or "empezar" in lower:
        return "quick-quote.html"
    if "seo" in lower:
        return "affordable-seo.html"
    if "ecommerce" in lower or "tienda" in lower:
        return "ecommerce-website-design.html"
    if "agentic" in lower or "editor" in lower or "demo" in lower:
        return "lightning-platform.html"
    if "soporte" in lower or "experto" in lower or "contacto" in lower:
        return "contact.html"
    if "blog" in lower or "artículo" in lower:
        return "blog.html"
    if "buscar" in lower:
        return "portfolio-search.html"
    return "quick-quote.html"


def clean_visible_text(text: str) -> str:
    replacements = {
        "Business success made easy": "Impulsa tu negocio sin líos",
        "Somos un equipo especializado en diseño web, SEO y crecimiento digital para negocios.": "Diseño web, SEO y soporte continuo para negocios que quieren crecer.",
        "Habla con S2Webs": "Habla con un experto",
        "Google PageSpeed Scores": "Puntuación Google PageSpeed",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def clean_section_title(title: str) -> str:
    lower = title.lower()
    if "trustpilot" in lower and "ecommerce" in lower:
        return "Reseñas ecommerce"
    if "trustpilot" in lower:
        return "Reseñas de clientes"
    return clean_visible_text(title)


def should_skip_visible_line(label: str | None, value: str) -> bool:
    combined = f"{label or ''} {value}".strip().lower()
    instruction_bits = [
        "[añadir",
        "mantener ",
        "sustituir ",
        "cuando estén escritos",
        "cuando estén disponibles",
        "usar proyectos reales",
        "nota: mantener",
    ]
    return any(bit in combined for bit in instruction_bits)


def render_labeled_line(label: str, value: str) -> str:
    if should_skip_visible_line(label, value):
        return ""
    value = clean_visible_text(value)
    esc = html.escape(value)
    normalized = label.lower()
    if normalized in {"h1"}:
        return f"<h3>{esc}</h3>"
    if normalized in {"título", "titulo"}:
        return f"<h3>{esc}</h3>"
    if normalized in {"subtítulo", "subtitulo"}:
        return f'<p class="lead">{esc}</p>'
    if normalized in {"texto", "nota", "texto destacado", "formulario", "cta"}:
        return paragraph(value)
    if "botón" in normalized or "boton" in normalized:
        return f'<p class="button-row"><a class="btn btn-inline" href="{action_href(value)}">{esc}</a></p>'
    if "cta" in normalized and value:
        return f'<p class="button-row"><a class="btn btn-inline" href="{action_href(value)}">{esc}</a></p>'
    if normalized in {"teléfono", "telefono", "email"}:
        return f'<p class="inline-detail"><strong>{html.escape(label)}:</strong> {esc}</p>'
    if normalized in {"referencia original"}:
        href = value.strip("`")
        return f'<p class="source-link"><a href="{html.escape(href)}">{html.escape(href)}</a></p>'
    return f'<p class="inline-detail"><strong>{html.escape(label)}:</strong> {esc}</p>'


def flush_list(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    items.clear()
    return f"<ul>{lis}</ul>"


def render_body(lines: list[str]) -> str:
    out: list[str] = []
    list_items: list[str] = []
    pending_group: str | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            out.append(flush_list(list_items))
            pending_group = None
            continue

        if line.startswith("- "):
            list_items.append(line[2:].strip())
            continue

        out.append(flush_list(list_items))

        if line.endswith("  "):
            line = line.rstrip()

        label_match = re.match(r"^([^:]{1,40}):\s*(.*)$", line)
        if label_match:
            label, value = label_match.groups()
            if value:
                out.append(render_labeled_line(label, value))
            else:
                pending_group = label
                out.append(f"<h4>{html.escape(label)}</h4>")
            continue

        numbered = re.match(r"^(\d{2}\.|\d{2} /|[0-9]+\.)\s*(.+)$", line)
        if numbered:
            out.append(f'<p class="step-line"><strong>{html.escape(numbered.group(1))}</strong> {html.escape(numbered.group(2))}</p>')
            continue

        if pending_group:
            out.append(f'<p><strong>{html.escape(pending_group)}:</strong> {html.escape(line)}</p>')
            pending_group = None
            continue

        if should_skip_visible_line(None, line):
            continue

        line = clean_visible_text(line)

        if len(line) <= 80 and not line.endswith("."):
            out.append(f"<h4>{html.escape(line)}</h4>")
        else:
            out.append(paragraph(line))

    out.append(flush_list(list_items))
    return "\n".join(chunk for chunk in out if chunk)


def section_variant(slug: str, index: int, title: str) -> str:
    t = title.lower()
    if "portfolio" in slug or "proyectos" in t or "casos" in t:
        return "portfolio-like"
    if slug in {"prices", "spark-package", "lightning-package", "shop-package", "quick-quote"}:
        return "pricing-like"
    if slug in {"faqs"} or "preguntas" in t:
        return "faq-like"
    if slug in {"compare"} or "compar" in t or "tabla" in t:
        return "compare-like"
    if slug in {"contact", "careers"} or "contacto" in t or "escríbenos" in t:
        return "form-like"
    if "cómo" in t or "como" in t or "3 " in t or "paso" in t:
        return "steps-like"
    if index % 3 == 1:
        return "split-like"
    if index % 3 == 2:
        return "cards-like"
    return "plain-like"


def render_sections(slug: str, sections: list[tuple[str, list[str]]]) -> str:
    rendered = []
    for idx, (title, lines) in enumerate(sections):
        if idx == 0 and title == "Contenido":
            continue
        title = clean_section_title(title)
        body = render_body(lines)
        if not body.strip() and title == "Contenido":
            continue
        variant = section_variant(slug, idx, title)
        rendered.append(
            f"""
      <section class="page-section {variant}">
        <div class="page section-inner">
          <h2>{html.escape(title)}</h2>
          <div class="rich-content">
            {body}
          </div>
        </div>
      </section>"""
        )
    return "\n".join(rendered)


def nav_html(active: str) -> str:
    main = [
        ("index.html", "Inicio", "home"),
        ("services.html", "Servicios", "services"),
        ("portfolio.html", "Portfolio", "portfolio"),
        ("why-it-seeze.html", "Por qué", "why-it-seeze"),
        ("prices.html", "Precios", "prices"),
        ("blog.html", "Blog", "blog"),
        ("contact.html", "Contacto", "contact"),
    ]
    links = []
    for href, label, slug in main:
        cls = ' class="active"' if active == slug else ""
        links.append(f'<a{cls} href="{href}">{label}</a>')
    return "\n          ".join(links)


def related_pages(active: str) -> str:
    items = []
    for slug in PAGE_ORDER:
        if slug == active:
            continue
        title = PAGE_TITLES.get(slug, slug.replace("-", " ").title())
        items.append(f'<a href="{slug_to_file(slug)}">{html.escape(title)}</a>')
    return "\n".join(items)


def build_page(slug: str, lines: list[str]) -> str:
    sections = split_sections(lines)
    flat = [line for _, group in sections for line in group]
    title = first_value(flat, ("H1:",)) or PAGE_TITLES.get(slug) or first_value(flat, ("Título:", "Titulo:")) or slug.replace("-", " ").title()
    subtitle = first_value(flat, ("Subtítulo:", "Subtitulo:", "Texto:"))

    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)} | S2Webs</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body class="page-{slug}">
    <header class="top page-top">
      <nav class="nav page" aria-label="Principal">
        <a class="brand" href="index.html" aria-label="S2Webs">
          <span class="brand-mark">S2</span>
          <span>Webs</span>
        </a>
        <div class="menu">
          {nav_html(slug)}
        </div>
        <div class="nav-cta">
          <a href="contact.html">Contactar</a>
          <a class="btn btn-small" href="quick-quote.html">Empieza</a>
        </div>
      </nav>
    </header>

    <main>
      <section class="internal-hero">
        <div class="page internal-hero-grid">
          <div>
            <p class="eyebrow">S2Webs</p>
            <h1>{html.escape(title)}</h1>
            {f'<p>{html.escape(subtitle)}</p>' if subtitle else ''}
            <div class="actions">
              <a class="btn" href="quick-quote.html">Da el primer paso</a>
              <a class="play-link" href="contact.html">Habla con un experto</a>
            </div>
          </div>
          <div class="hero-panel">
            <span>Agentic</span>
            <strong>90-100</strong>
            <p>Puntuación Google PageSpeed</p>
          </div>
        </div>
      </section>
      {render_sections(slug, sections)}
    </main>

    <footer class="footer">
      <div class="page footer-grid">
        <div class="footer-links">
          <a href="index.html">Inicio</a>
          <a href="services.html">Servicios</a>
          <a href="portfolio.html">Portfolio</a>
          <a href="prices.html">Precios</a>
          <a href="contact.html">Contacto</a>
        </div>
        <div>
          <p>S2Webs crea webs rápidas, seguras y fáciles de gestionar con tecnología Agentic.</p>
          <p>Diseño web, SEO, ecommerce y soporte continuo para negocios que quieren crecer.</p>
        </div>
        <div class="footer-brand">
          <a class="brand" href="index.html"><span class="brand-mark">S2</span><span>Webs</span></a>
          <p>Webs sin líos.</p>
        </div>
      </div>
    </footer>
  </body>
</html>
"""


def main() -> None:
    text = CONTENT.read_text(encoding="utf-8")
    pages = parse_markdown(text)
    for slug in PAGE_ORDER:
        if slug not in pages:
            continue
        (ROOT / slug_to_file(slug)).write_text(build_page(slug, pages[slug]), encoding="utf-8")
        print(slug_to_file(slug))


if __name__ == "__main__":
    main()
