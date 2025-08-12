from datetime import date
from decimal import Decimal, InvalidOperation
import os
from typing import Optional

from .. import db
from ..models import Marca, Categoria, Loja, Produto, Preco, Historico

def _first_or_create(model, **kwargs):
    inst = model.query.filter_by(**kwargs).first()
    if inst:
        return inst
    inst = model(**kwargs)
    db.session.add(inst)
    db.session.flush()
    return inst

def upsert_loja(nome: str, link: str, logo_url: str) -> Loja:
    loja = Loja.query.filter_by(nome=nome).first()
    if loja:
        loja.link = link
        loja.logo_url = logo_url
        return loja
    return _first_or_create(Loja, nome=nome, link=link, logo_url=logo_url)

def upsert_produto(nome: str, descricao: str, marca_nome: str,
                   categoria_nome: str, imagem_url: str) -> Produto:
    marca = _first_or_create(Marca, nome=marca_nome)
    categoria = _first_or_create(Categoria, nome=categoria_nome)

    prod = Produto.query.filter_by(
        nome=nome[:150],
        id_marca=marca.id,
        id_categoria=categoria.id
    ).first()
    if prod:
        prod.descricao = descricao
        prod.imagem_url = imagem_url
        return prod

    prod = Produto(
        nome=nome[:150],
        descricao=descricao,
        id_marca=marca.id,
        id_categoria=categoria.id,
        imagem_url=imagem_url
    )
    db.session.add(prod)
    db.session.flush()
    return prod

def add_preco(produto_id: int, loja_id: int, preco_original: Decimal,
              preco_atual: Decimal, desconto: Optional[Decimal],
              url_produto: str, data_ref: date):
    p = Preco(
        id_produto=produto_id, id_loja=loja_id,
        preco_original=preco_original, preco_atual=preco_atual,
        desconto=desconto, url_produto=url_produto[:500],
        data_preco=data_ref
    )
    db.session.add(p)

def upsert_historico(produto_id: int, data_ref: date, preco: Decimal):
    h = Historico.query.filter_by(id_produto=produto_id, data=data_ref).first()
    if h:
        h.preco = preco
    else:
        db.session.add(Historico(id_produto=produto_id, data=data_ref, preco=preco))

# ---------- conversão de moeda ----------
def _to_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")

def convert_to_brl(valor: Decimal, moeda: str) -> Decimal:
    moeda = (moeda or "BRL").upper()
    if moeda == "BRL":
        return valor
    usd_brl = Decimal(os.getenv("USD_BRL", "6.00"))   # ajuste via env
    pyg_brl = Decimal(os.getenv("PYG_BRL", "0.00070"))
    if moeda == "USD":
        return (valor * usd_brl).quantize(Decimal("0.01"))
    if moeda in ("PYG", "GS"):
        return (valor * pyg_brl).quantize(Decimal("0.01"))
    return valor  # fallback

def ingest_item(item: dict, loja_info: dict, categoria_padrao: str):
    """
    item esperado: {
      nome, descricao, preco_atual, preco_original, url, img,
      marca (opcional), ean (opcional), moeda ("USD","PYG","BRL")
    }
    """
    loja = upsert_loja(loja_info["nome"], loja_info["link"], loja_info["logo"])
    marca_nome = item.get("marca") or _guess_brand(item["nome"]) or "Genérica"
    prod  = upsert_produto(
        nome=item["nome"],
        descricao=(item.get("descricao") or item["nome"])[:10000],
        marca_nome=marca_nome,
        categoria_nome=categoria_padrao,
        imagem_url=item.get("img") or ""
    )

    moeda = (item.get("moeda") or "BRL").upper()
    preco_atual_src    = _to_decimal(item.get("preco_atual"))
    preco_original_src = _to_decimal(item.get("preco_original") or item.get("preco_atual"))
    # converte para BRL antes de gravar
    preco_atual_brl    = convert_to_brl(preco_atual_src, moeda)
    preco_original_brl = convert_to_brl(preco_original_src, moeda)

    desconto = None
    if preco_original_brl and preco_original_brl > 0:
        desconto = ((Decimal("1") - (preco_atual_brl / preco_original_brl)) * Decimal("100")).quantize(Decimal("0.01"))

    today = date.today()
    add_preco(prod.id, loja.id, preco_original_brl, preco_atual_brl, desconto, item["url"], today)
    upsert_historico(prod.id, today, preco_atual_brl)

def commit():
    db.session.commit()

def _guess_brand(nome: str) -> Optional[str]:
    common = ["Apple","Samsung","Xiaomi","Asus","Logitech","Sony","Lenovo","Acer","MSI","Dell","HP","Corsair","Kingston","Seagate","Western Digital","Sandisk","Huawei","Motorola","Canon","Nikon","JBL","Razer"]
    n = nome.lower()
    for b in common:
        if b.lower() in n:
            return b
    return None
