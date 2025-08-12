import re, time, random, httpx
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

def fetch_mega_list(category_url_tmpl: str, page: int, timeout=30) -> str:
    time.sleep(random.uniform(0.4, 1.0))
    url = category_url_tmpl.format(page=page)
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=HDRS) as c:
        r = c.get(url); r.raise_for_status()
        return r.text

def parse_mega(html: str):
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".product-card, .item-product, article.product, .product")
    for c in cards:
        name_el = c.select_one(".title, .product-title, h3, h2")
        price_el = c.select_one(".price, .price-final, .current-price")
        a = c.select_one("a[href]")
        img_el = c.select_one("img")

        if not name_el or not price_el:
            continue

        nome = name_el.get_text(strip=True)
        preco = _clean_price(price_el.get_text())
        if not nome or not preco:
            continue

        old_el = c.select_one(".price-old, .from, .original-price")
        preco_de = _clean_price(old_el.get_text()) if old_el else preco
        url = a["href"] if a else ""
        img = (img_el.get("src") or img_el.get("data-src") or "") if img_el else ""

        yield {
            "nome": nome,
            "descricao": nome,
            "preco_atual": preco,
            "preco_original": preco_de,
            "url": url,
            "img": img,
            "moeda": "USD"
        }
