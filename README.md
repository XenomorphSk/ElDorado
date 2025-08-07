Sites base:
https://www.comprasparaguai.com.br/
https://www.kabum.com.br/?utm_id=22203197197&gad_source=1&gad_campaignid=22203197197&gclid=Cj0KCQjwndHEBhDVARIsAGh0g3Ay6Jr8TEhSxNRGp8M0Wc8KQrxmuntuPtHL7pdh2CnXzX2eQmiFhmoaAuQoEALw_wcB


# 🛒 Projeto: Market Dominator – Comparador de Preços Superior ao Compras Paraguai

> Sistema completo para comparar preços de eletrônicos e produtos importados com scraping, back-end em Flask, banco MySQL e frontend clean estilo Kabum. Foco em performance, UX e scraping inteligente.

---

## 🔍 Objetivo do Projeto

Desenvolver uma **plataforma web** para pesquisa e comparação de preços de produtos vendidos no Paraguai e em sites importadores. A plataforma terá foco em velocidade, design limpo e scraping eficiente de múltiplas fontes, superando o desempenho e usabilidade do **Compras Paraguai**.

---

## ✅ Requisitos Funcionais

1. **Busca de produtos** por nome ou categoria.
2. **Comparação automática de preços** entre diferentes lojas (com ordenação).
3. Página individual para cada produto, com:
   - Nome, imagem, descrição
   - Lista de lojas com preços e links
   - Gráfico de histórico de preço
4. **Scraping automático diário** (ou sob demanda) para atualizar preços.
5. Cadastro de produtos e lojas via painel admin (futuro).
6. Filtro por:
   - Loja
   - Preço
   - Categoria
   - Marca
7. Sistema de favoritos / observação de produto.
8. Integração com alertas de preço por e-mail (futuro).
9. Página de destaques (novidades, mais baratos, promoções).
10. API REST para consumo dos dados (opcional, futuro).

---

## 🚫 Requisitos Não Funcionais

- **Performance**: busca com resposta em menos de 1 segundo.
- **Escalabilidade**: estrutura pronta para escalar scraping e banco.
- **SEO-friendly**: URLs amigáveis, meta-tags otimizadas.
- **Design clean e responsivo**: baseado em Kabum, com foco mobile-first.
- **Segurança**:
  - Proteção contra scraping externo e ataques de injeção
  - Sanitização de entradas
- **Manutenibilidade**: código modular, documentação clara, uso de Blueprints no Flask.
- **Scraper robusto**:
  - Detecção de mudanças de layout das lojas
  - Captura de erros e logs de scraping
- **Deployável facilmente** em servidor Linux ou Render.com

---

## 🧠 Lógica de Funcionamento

### Scraping Engine (Python)
- Utiliza `requests`, `BeautifulSoup`, e/ou `Selenium` se necessário
- Cada loja terá seu próprio módulo de scraping (`scrapers/loja_xyz.py`)
- Salva/atualiza dados no banco via SQLAlchemy
- Executado por `scheduler` (Ex: cron job, Celery, APScheduler)

### Backend (Flask)
- Roteamento REST
- Padrão MVC + Blueprints
- ORM com SQLAlchemy + conexão MySQL
- Sistema de cache (opcional: Redis)
- Integração com scripts de scraping

### Frontend (HTML, CSS, JS)
- Tema inspirado no Kabum
- Responsivo (mobile e desktop)
- Páginas:
  - Home (produtos em destaque)
  - Resultado de busca
  - Página do produto
  - Admin (painel de controle - básico)

---

## 🧱 Lógica do Banco de Dados (Modelo Inicial)

### Tabelas Principais

```
Produto
- id (PK)
- nome
- categoria
- marca
- descricao
- imagem_url
- criado_em
- atualizado_em

Loja
- id (PK)
- nome
- site_url
- logo_url

Preco
- id (PK)
- produto_id (FK → Produto)
- loja_id (FK → Loja)
- preco
- url_produto_loja
- data_coleta

Categoria
- id (PK)
- nome

Usuario (futuro)
- id (PK)
- email
- senha_hash
- data_cadastro

Favorito (futuro)
- id (PK)
- usuario_id (FK → Usuario)
- produto_id (FK → Produto)
```

### Relacionamentos
- **Produto : Preco** → 1:N  
- **Loja : Preco** → 1:N  
- **Produto : Categoria** → N:1  
- **Usuario : Favorito : Produto** → N:N  

---

## 🛠️ Tecnologias Utilizadas

| Camada | Ferramenta |
|--------|------------|
| Frontend | HTML + TailwindCSS ou Bootstrap, JS Vanilla ou VueJS (opcional) |
| Backend | Flask (Python) |
| Scraping | BeautifulSoup, Requests, Selenium (se necessário) |
| Banco de Dados | MySQL (MariaDB) |
| ORM | SQLAlchemy |
| Scheduler | Cron / APScheduler |
| Controle de versão | Git + GitHub |
| Deploy | VPS Linux, Render.com, Railway, etc |

---

## 🧪 Possíveis Funcionalidades Futuras

- API pública de consulta de preços
- Registro/login e painel do usuário
- Alertas de queda de preço
- Histórico de preço com gráficos
- Sistema de reviews das lojas
- Dashboard de scraping com logs, status e erros
- Cluster de scraping paralelo para evitar bloqueio

---

## 🚀 Como Começar o Desenvolvimento

1. Crie o banco de dados MySQL local com as tabelas acima
2. Estruture o Flask com Blueprints (ex: `/routes`, `/models`, `/scrapers`)
3. Faça 1 scraper funcional (por ex. Mega Eletrônicos)
4. Crie a rota `/busca` que busca produtos e exibe os preços
5. Crie a interface básica (HTML/CSS) baseada na Kabum
6. Integre a busca → rota Flask → consulta SQL → exibição na página
