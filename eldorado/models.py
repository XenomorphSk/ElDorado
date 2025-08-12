from . import db
from sqlalchemy import UniqueConstraint

class Marca(db.Model):
    __tablename__ = "marca"
    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

class Produto(db.Model):
    __tablename__ = "produto"
    id                 = db.Column(db.Integer, primary_key=True)
    nome               = db.Column(db.String(150), nullable=False)
    descricao          = db.Column(db.Text, nullable=False)
    id_marca           = db.Column(db.Integer, db.ForeignKey("marca.id"), nullable=False)
    id_categoria       = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    imagem_url         = db.Column(db.Text, nullable=False)
    data_criacao       = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    ultima_atualizacao = db.Column(db.DateTime, nullable=False,
                                   server_default=db.text("CURRENT_TIMESTAMP"),
                                   server_onupdate=db.text("CURRENT_TIMESTAMP"))

class Loja(db.Model):
    __tablename__ = "loja"
    id       = db.Column(db.Integer, primary_key=True)
    nome     = db.Column(db.String(100), nullable=False, unique=True)
    link     = db.Column(db.String(500), nullable=False)
    logo_url = db.Column(db.String(500), nullable=False)

class Preco(db.Model):
    __tablename__ = "preco"
    id             = db.Column(db.Integer, primary_key=True)
    id_produto     = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    id_loja        = db.Column(db.Integer, db.ForeignKey("loja.id"), nullable=False)
    preco_original = db.Column(db.Numeric(10,2), nullable=False)
    preco_atual    = db.Column(db.Numeric(10,2), nullable=False)
    desconto       = db.Column(db.Numeric(5,2))
    url_produto    = db.Column(db.String(500), nullable=False)
    data_preco     = db.Column(db.Date, nullable=False)
    __table_args__ = (
        db.Index("ix_preco_prod_loja", "id_produto", "id_loja"),
        db.Index("ix_preco_data", "data_preco"),
    )

class Historico(db.Model):
    __tablename__ = "historico"
    id         = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    data       = db.Column(db.Date, nullable=False)
    preco      = db.Column(db.Numeric(10,2), nullable=False)
    __table_args__ = (UniqueConstraint("id_produto","data", name="uq_produto_data"),)
