import click, pathlib
from flask import Flask
from .pipeline import ingest_item, commit
from .adapters.kabum import fetch_kabum_list, parse_kabum
from .adapters.cellshop import fetch_cellshop_list, parse_cellshop
from .adapters.nissei import fetch_nissei_list, parse_nissei
from .adapters.mega import fetch_mega_list, parse_mega

def register_cli(app: Flask):
    @app.cli.group("scrape")
    def scrape_group():
        """Comandos de scraping ElDorado."""

    # --- KaBuM (teste) ---
    @scrape_group.command("kabum")
    @click.option("--pages", default=1)
    @click.option("--url", default="https://www.kabum.com.br/hardware/placa-de-video-vga?page={page}")
    @click.option("--dump-html", is_flag=True)
    def scrape_kabum(pages, url, dump_html):
        loja = {"nome": "KaBuM!", "link": "https://www.kabum.com.br", "logo": "https://www.kabum.com.br/logo.png"}
        categoria = "Placa de Vídeo"
        _run_generic("kabum", pages, url, dump_html, loja, categoria, fetch_kabum_list, parse_kabum)

    # --- Cellshop (PY) ---
    @scrape_group.command("cellshop")
    @click.option("--pages", default=1)
    @click.option("--url", default="https://www.cellshop.com/categoria?page={page}")
    @click.option("--categoria", default="Eletrônicos")
    @click.option("--dump-html", is_flag=True)
    def scrape_cellshop(pages, url, categoria, dump_html):
        loja = {"nome": "Cellshop", "link": "https://www.cellshop.com", "logo": "https://www.cellshop.com/logo.png"}
        _run_generic("cellshop", pages, url, dump_html, loja, categoria, fetch_cellshop_list, parse_cellshop)

    # --- Nissei (PY) ---
    @scrape_group.command("nissei")
    @click.option("--pages", default=1)
    @click.option("--url", default="https://www.nissei.com/categoria?page={page}")
    @click.option("--categoria", default="Eletrônicos")
    @click.option("--dump-html", is_flag=True)
    def scrape_nissei(pages, url, categoria, dump_html):
        loja = {"nome": "Nissei", "link": "https://www.nissei.com", "logo": "https://www.nissei.com/logo.png"}
        _run_generic("nissei", pages, url, dump_html, loja, categoria, fetch_nissei_list, parse_nissei)

    # --- Mega Eletrônicos (PY) ---
    @scrape_group.command("mega")
    @click.option("--pages", default=1)
    @click.option("--url", default="https://www.megaeletronicos.com/categoria?page={page}")
    @click.option("--categoria", default="Eletrônicos")
    @click.option("--dump-html", is_flag=True)
    def scrape_mega(pages, url, categoria, dump_html):
        loja = {"nome": "Mega Eletrônicos", "link": "https://www.megaeletronicos.com", "logo": "https://www.megaeletronicos.com/logo.png"}
        _run_generic("mega", pages, url, dump_html, loja, categoria, fetch_mega_list, parse_mega)

def _run_generic(tag, pages, url, dump_html, loja, categoria, fetch_fn, parse_fn):
    import pathlib
    dump_dir = pathlib.Path("_dump"); 
    if dump_html: dump_dir.mkdir(exist_ok=True)
    total = 0
    for p in range(1, pages+1):
        html = fetch_fn(url, p)
        if dump_html:
            (dump_dir / f"{tag}_p{p}.html").write_text(html, encoding="utf-8")
        count = 0
        for item in parse_fn(html):
            ingest_item(item, loja, categoria)
            total += 1; count += 1
        click.echo(f"{tag} | página {p}: {count} itens.")
    commit()
    click.echo(f"[OK] {loja['nome']}: {total} itens inseridos/atualizados.")
