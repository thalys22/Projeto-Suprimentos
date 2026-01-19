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
    un TEXT,
    preco_unitario NUMERIC,
    total NUMERIC,
    data_movimento TIMESTAMP,
    centro_custo TEXT,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    regional TEXT
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
    regional TEXT
);

CREATE TABLE IF NOT EXISTS base_cesta_apropriacoes (
    id SERIAL PRIMARY KEY,
    un TEXT,
    quantidade NUMERIC,
    preco_unitario NUMERIC,
    total NUMERIC,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    centro_custo TEXT,
    regional TEXT
);

CREATE TABLE IF NOT EXISTS solicitacoes (
    id SERIAL PRIMARY KEY,
    numero_solicitacao INTEGER,
    codigo_obra INTEGER,
    obra TEXT,
    codigo_insumo INTEGER,
    descricao_insumo TEXT,
    data_solicitacao TIMESTAMP,
    previsao_de_entrega TIMESTAMP,
    data_pedido TIMESTAMP,
    data_entrega_na_obra TIMESTAMP,
    numero_pedido INTEGER,
    codigo_fornecedor INTEGER,
    nota_fiscal TEXT,
    comprador TEXT,
    dias INTEGER,
    urgencia TEXT,
    centro_custo TEXT,
    unidade TEXT

);

CREATE TABLE IF NOT EXISTS config_regionais (
    regional TEXT PRIMARY KEY,
    unidades INTEGER,
    ano_referencia INTEGER
);

CREATE TABLE IF NOT EXISTS metas_incc (
    mes_referencia DATE PRIMARY KEY,
    evolucao_mensal NUMERIC,
    acumulado_12_meses NUMERIC
);

-- Inserção inicial das regionais
INSERT INTO config_regionais (regional, unidades, ano_referencia) 
VALUES ('SE', 1000, 2026), ('BA', 435, 2026)
ON CONFLICT (regional) DO UPDATE SET unidades = EXCLUDED.unidades, ano_referencia = EXCLUDED.ano_referencia;

-- Inserção das metas INCC-M (Valores de referência reduzidos em 50% conforme solicitado)
-- Ex: dez/25 ref 0.21% -> meta 0.105% (0.00105)
INSERT INTO metas_incc (mes_referencia, evolucao_mensal, acumulado_12_meses) VALUES
('2025-12-01', 0.00105, 0.0305),
('2025-11-01', 0.0014,  0.03205),
('2025-10-01', 0.00105, 0.0329),
('2025-09-01', 0.00105, 0.03535),
('2025-08-01', 0.0035,  0.03745),
('2025-07-01', 0.00455, 0.03715),
('2025-06-01', 0.0048,  0.03595),
('2025-05-01', 0.0013,  0.03585),
('2025-04-01', 0.00295, 0.0376),
('2025-03-01', 0.0019,  0.0366),
('2025-02-01', 0.00255, 0.0359),
('2025-01-01', 0.00355, 0.03425),
('2024-12-01', 0.00255, 0.0317)
ON CONFLICT (mes_referencia) DO UPDATE SET 
    evolucao_mensal = EXCLUDED.evolucao_mensal, 
    acumulado_12_meses = EXCLUDED.acumulado_12_meses;

"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("Tabelas e metas (50%) atualizadas!")
