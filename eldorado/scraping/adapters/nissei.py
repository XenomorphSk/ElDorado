import re, time, random, httpx, json
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HDRS = {"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}

def _clean_price(t):
    t = re.sub(r"[^0-9,.\-]", "", t or "")
    if t.count(",")==1 and t.count(".")==0: t = t.replace(",", ".")
    if t.count(",")==1 and t.count(".")>=1: t = t.replace(".","").replace(",",".")
    try: return float(t)
    except: return None

def fetch_nissei_list(category_url_tmpl: str, page: int, timeout=40) -> str:
    # algumas páginas carregam com JS; tentamos HTML direto primeiro
    time.sleep(random.uniform(0.5, 1.2))
    url = category_url_tmpl.format(page=page)
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=HDRS) as c:
        r = c.get(url); r.raise_for_status()
        return r.text

def parse_nissei(html: str):
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".product-card, .productCard, article.product, .grid__item")
    yielded = False
    for c in cards:
        name_el = c.select_one(".product-title, .product__title, h3, h2")
        price_el = c.select_one(".price-final, .price, .price__regular, .money")
        a = c.select_one("a[href]")
        img_el = c.select_one("img")

        if not name_el or not price_el:
            continue

        nome = name_el.get_text(strip=True)
        preco = _clean_price(price_el.get_text())
        if not nome or not preco:
            continue

        old_el = c.select_one(".price-old, .price__sale, .compare-at")
        preco_de = _clean_price(old_el.get_text()) if old_el else preco
        url = a["href"] if a else ""
        img = (img_el.get("src") or img_el.get("data-src") or "") if img_el else ""

        yield {
            "nome": name,
            "descricao": name,
            "preco_atual": price_f,
            "preco_original": price_f,
            "url": url,
            "img": img,
            "moeda": "PYG"   # <- antes estava USD
        }

        yielded = True

    if yielded:
        return

    # fallback: tentar JSON-LD (algumas vitrines usam)
    for tag in soup.select("script[type='application/ld+json']"):
        try:
            data = json.loads(tag.string or "")
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if node.get("@type") in ("Product","Offer","AggregateOffer"):
                name = node.get("name")
                offers = node.get("offers") or {}
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                price = offers.get("price") or offers.get("lowPrice")
                url = node.get("url") or ""
                img = ""
                if isinstance(node.get("image"), list) and node["image"]:
                    img = node["image"][0]
                elif isinstance(node.get("image"), str):
                    img = node["image"]
                if name and price:
                    try:
                        price_f = float(str(price))
                    except Exception:
                        continue
                    yield {
                        "nome": name,
                        "descricao": name,
                        "preco_atual": price_f,
                        "preco_original": price_f,
                        "url": url,
                        "img": img,
                        "moeda": "USD"
                    }
