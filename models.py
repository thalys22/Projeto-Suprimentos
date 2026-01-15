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

CREATE TABLE IF NOT EXISTS base_cesta_apropriacoes (
    id SERIAL PRIMARY KEY,
    un TEXT,
    quantidade NUMERIC,
    preco_unitario NUMERIC,
    total NUMERIC,
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
    FOREIGN KEY (codigo_fornecedor) REFERENCES fornecedores (codigo_fornecedor),
    FOREIGN KEY (codigo_insumo) REFERENCES grupo_insumo (codigo_insumo)

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

-- Inserção inicial das metas INCC-M (2025)
INSERT INTO metas_incc (mes_referencia, evolucao_mensal, acumulado_12_meses) VALUES
('2025-12-01', 0.0021, 0.0610),
('2025-11-01', 0.0028, 0.0641),
('2025-10-01', 0.0021, 0.0658),
('2025-09-01', 0.0021, 0.0707),
('2025-08-01', 0.0070, 0.0749),
('2025-07-01', 0.0091, 0.0743),
('2025-06-01', 0.0096, 0.0719),
('2025-05-01', 0.0026, 0.0717),
('2025-04-01', 0.0059, 0.0752),
('2025-03-01', 0.0038, 0.0732),
('2025-02-01', 0.0051, 0.0718),
('2025-01-01', 0.0071, 0.0685)
ON CONFLICT (mes_referencia) DO NOTHING;

"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("Tabelas e dados iniciais criados!")
