import re, json, random, time
import httpx
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HDRS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
}

def _clean_price(t):
    t = re.sub(r"[^0-9,.\-]", "", t or "")
    if t.count(",")==1 and t.count(".")==0: t = t.replace(",", ".")
    if t.count(",")==1 and t.count(".")>=1: t = t.replace(".","").replace(",",".")
    try: return float(t)
    except: return None

def fetch_kabum_list(category_url_tmpl: str, page: int, timeout=30, jitter=True) -> str:
    url = category_url_tmpl.format(page=page)
    # pequeno jitter ajuda a não tomar bloqueio
    if jitter: time.sleep(random.uniform(0.5, 1.2))
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=HDRS, http2=True) as c:
        r = c.get(url)
        r.raise_for_status()
        return r.text

def _parse_cards_dom(soup: BeautifulSoup):
    # Várias tentativas de seletor
    cards = (
        soup.select("[data-testid='product-card']") or
        soup.select("[data-cy='product-card']") or
        soup.select("article[data-sku]") or
        soup.select(".productCard, .product-card, .sc-d")  # fallback genérico
    )
    for c in cards:
        # Nome
        name_el = (c.select_one("[data-testid='product-card::name']") or
                   c.select_one("[data-cy='product-name']") or
                   c.select_one(".nameCard, .product-name, h2, h3"))
        if not name_el:
            continue
        nome = name_el.get_text(strip=True)
        if not nome:
            continue

        # Preços
        p_atual_el = (c.select_one("[data-testid='product-card::price']") or
                      c.select_one("[data-cy='price-final']") or
                      c.select_one(".priceCard, .price, .final-price"))
        p_de_el    = (c.select_one("[data-testid='product-card::price-old']") or
                      c.select_one("[data-cy='price-old']") or
                      c.select_one(".oldPrice, .from, .original-price"))

        preco_atual = _clean_price(p_atual_el.get_text()) if p_atual_el else None
        preco_de    = _clean_price(p_de_el.get_text()) if p_de_el else preco_atual

        # URL
        a = c.find("a", href=True)
        url = ("https://www.kabum.com.br"+a["href"]) if a and a["href"].startswith("/") else (a["href"] if a else "")

        # Imagem
        img_el = c.find("img")
        img = (img_el.get("src") or img_el.get("data-src") or "") if img_el else ""

        if preco_atual and nome:
            yield {
                "nome": nome,
                "descricao": nome,
                "preco_atual": preco_atual,
                "preco_original": preco_de,
                "url": url,
                "img": img
            }

def _parse_jsonld(soup: BeautifulSoup):
    # Muitas listagens trazem JSON‑LD com Product/Offer
    for tag in soup.select("script[type='application/ld+json']"):
        try:
            data = json.loads(tag.string or "")
        except Exception:
            continue
        # Pode vir como objeto único ou lista
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            typ = node.get("@type") or node.get("@graph", [{}])[0].get("@type")
            # Normaliza quando @graph existe
            if "@graph" in node:
                for g in node["@graph"]:
                    if g.get("@type") in ("Product","Offer","AggregateOffer"):
                        yield from _from_ld_node(g, node_base=node)
            else:
                if typ in ("Product","Offer","AggregateOffer"):
                    yield from _from_ld_node(node)
        # continua próximo script
    return

def _from_ld_node(node, node_base=None):
    # Extrai informações relevantes de Product/Offer
    nome = node.get("name") or (node_base or {}).get("name")
    img  = ""
    if isinstance(node.get("image"), list) and node["image"]:
        img = node["image"][0]
    elif isinstance(node.get("image"), str):
        img = node["image"]
    url = node.get("url") or (node_base or {}).get("url") or ""
    offers = node.get("offers") or {}
    if isinstance(offers, list) and offers:
        offers = offers[0]
    price = offers.get("price") or offers.get("lowPrice")
    currency = offers.get("priceCurrency")
    # Só emite se tiver preço e nome
    if price and nome:
        try:
            preco_atual = float(price)
        except Exception:
            return
        yield {
            "nome": nome,
            "descricao": nome,
            "preco_atual": preco_atual,
            "preco_original": preco_atual,
            "url": url,
            "img": img
        }

def parse_kabum(html: str):
    soup = BeautifulSoup(html, "lxml")
    # 1) tenta DOM
    yielded = False
    for item in _parse_cards_dom(soup):
        yielded = True
        yield item
    if yielded:
        return
    # 2) fallback JSON‑LD
    for item in _parse_jsonld(soup):
        yielded = True
        yield item
