from sqlalchemy import text
from db import engine

sql = """
-- DIMENSÕES
CREATE TABLE IF NOT EXISTS fornecedores (
    codigo_fornecedor INTEGER PRIMARY KEY,
    fornecedor TEXT
);

CREATE TABLE IF NOT EXISTS grupo_insumo (
    codigo_insumo INTEGER PRIMARY KEY,
    insumo TEXT,
    indice_grupo INTEGER,
    grupo_de_insumo TEXT
);

-- FATOS
CREATE TABLE IF NOT EXISTS nf_movimentos (
    id SERIAL PRIMARY KEY,
    movimento TEXT,
    codigo_fornecedor INTEGER,
    quantidade NUMERIC,
    unidade TEXT,
    preco_unitario NUMERIC,
    total NUMERIC,
    data_movimento TIMESTAMP,
    centro_custo TEXT,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    regional TEXT,
    FOREIGN KEY (codigo_fornecedor) REFERENCES fornecedores (codigo_fornecedor),
    FOREIGN KEY (codigo_insumo) REFERENCES grupo_insumo (codigo_insumo)
);

CREATE TABLE IF NOT EXISTS nfse_medicoes (
    id SERIAL PRIMARY KEY,
    descricao_insumo TEXT,
    un TEXT,
    quantidade NUMERIC,
    preco_unitario NUMERIC,
    total NUMERIC,
    data_movimento TIMESTAMP,
    centro_custo TEXT,
    codigo_fornecedor INTEGER,
    regional TEXT,
    FOREIGN KEY (codigo_fornecedor) REFERENCES fornecedores (codigo_fornecedor)
);

CREATE TABLE IF NOT EXISTS cesta_apropriacoes (
    id SERIAL PRIMARY KEY,
    un TEXT,
    quantidade NUMERIC,
    preco_unit_medio NUMERIC,
    preco_total NUMERIC,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    centro_custo TEXT,
    regional TEXT,
    FOREIGN KEY (codigo_insumo) REFERENCES grupo_insumo (codigo_insumo)
);

CREATE TABLE IF NOT EXISTS solicitacoes (
    id SERIAL PRIMARY KEY,
    numero_solicitacao INTEGER,
    codigo_obra INTEGER,
    obra TEXT,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    data_solicitacao TIMESTAMP,
    data_chegada_obra TIMESTAMP,
    numero_pedido INTEGER,
    data_pedido TIMESTAMP,
    codigo_fornecedor INTEGER,
    nota_fiscal TEXT,
    dias INTEGER,
    urgencia TEXT,
    centro_custo TEXT,
    FOREIGN KEY (codigo_fornecedor) REFERENCES fornecedores (codigo_fornecedor),
    FOREIGN KEY (codigo_insumo) REFERENCES grupo_insumo (codigo_insumo)
);
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("Tabelas criadas !")
