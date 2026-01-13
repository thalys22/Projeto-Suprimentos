from sqlalchemy import text
from db import engine

sql = """
CREATE TABLE IF NOT EXISTS fornecedores (
    codigo INTEGER PRIMARY KEY,
    fornecedor TEXT
);

CREATE TABLE IF NOT EXISTS nf_movimentos (
    movimento TEXT,
    fornecedor INTEGER,
    ncm TEXT,
    historico_da_operacao TEXT,
    quantidade NUMERIC,
    unidade TEXT,
    preco_unitario NUMERIC,
    quantidade_unidade_basica NUMERIC,
    unidade_basica TEXT,
    preco_unitario_2 NUMERIC,
    total NUMERIC,
    data_movimento TIMESTAMP,
    centro_custo TEXT,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    regional TEXT
);

CREATE TABLE IF NOT EXISTS nfse_medicoes (
    referencia TEXT,
    descricao TEXT,
    un TEXT,
    ad TEXT,
    contratada NUMERIC,
    acum_anterior NUMERIC,
    medida NUMERIC,
    exe NUMERIC,
    preco_unitario NUMERIC,
    acum_anterior_2 NUMERIC,
    medicao NUMERIC,
    data_movimento TIMESTAMP,
    centro_custo TEXT,
    codigo_fornecedor INTEGER,
    descricao_fornecedor TEXT,
    regional TEXT
);

CREATE TABLE IF NOT EXISTS cesta_apropriacoes (
    un TEXT,
    quantidade NUMERIC,
    preco_unit_medio NUMERIC,
    preco_total NUMERIC,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    centro_custo TEXT,
    regional TEXT
);

CREATE TABLE IF NOT EXISTS solicitacoes (
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
    fornecedor TEXT,
    nota_fiscal TEXT,
    dias INTEGER,
    urgencia TEXT
);
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("✅ Tabelas criadas com sucesso")
