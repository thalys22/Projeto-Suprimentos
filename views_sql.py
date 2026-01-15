# views_sql.py

VIEW_CURVA_ABC = """
CREATE OR REPLACE VIEW view_curva_abc_insumos AS
WITH total_geral AS (
    SELECT SUM(total) as valor_global
    FROM base_cesta_apropriacoes
),
insumos_agrupados AS (
    SELECT 
        codigo_insumo::TEXT,
        descricao_insumo,
        SUM(quantidade) as qtd_total,
        SUM(total) as valor_total_insumo
    FROM base_cesta_apropriacoes
    GROUP BY 1, 2
),
calculo_contribuicao AS (
    SELECT 
        ia.*,
        (ia.valor_total_insumo / tg.valor_global) as contribuicao_percentual
    FROM insumos_agrupados ia, total_geral tg
),
calculo_acumulado AS (
    SELECT 
        *,
        SUM(contribuicao_percentual) OVER (ORDER BY contribuicao_percentual DESC) as contribuicao_acumulada
    FROM calculo_contribuicao
)
SELECT 
    *,
    CASE 
        WHEN contribuicao_acumulada <= 0.80 THEN 'A'
        WHEN contribuicao_acumulada <= 0.95 THEN 'B'
        ELSE 'C'
    END as classe_abc
FROM calculo_acumulado;
"""

VIEW_CONSOLIDADO_PRECOS = """
CREATE OR REPLACE VIEW view_consolidado_precos AS
WITH solicitacoes_urgentes AS (
    SELECT DISTINCT 
        codigo_insumo::TEXT, 
        centro_custo 
    FROM solicitacoes 
    WHERE urgencia = 'Urgente'
),
movimentos_filtrados AS (
    SELECT 
        nf.data_movimento,
        nf.codigo_insumo::TEXT,
        nf.descricao_insumo,
        nf.quantidade,
        nf.preco_unitario,
        nf.total,
        nf.centro_custo,
        nf.regional,
        nf.codigo_fornecedor::TEXT as codigo_fornecedor,
        'NF' as origem
    FROM nf_movimentos nf
    LEFT JOIN solicitacoes_urgentes su ON nf.codigo_insumo::TEXT = su.codigo_insumo AND nf.centro_custo = su.centro_custo
    WHERE su.codigo_insumo IS NULL
    
    UNION ALL
    
    SELECT 
        se.data_movimento,
        NULL as codigo_insumo, 
        se.descricao_insumo,
        se.quantidade,
        se.preco_unitario,
        se.total,
        se.centro_custo,
        se.regional,
        se.codigo_fornecedor::TEXT as codigo_fornecedor,
        'NFSE' as origem
    FROM nfse_medicoes se
)
SELECT * FROM movimentos_filtrados;
"""

VIEW_INFLACAO_POR_INSUMO = """
CREATE OR REPLACE VIEW view_inflacao_por_insumo AS
WITH preco_medio_mensal AS (
    SELECT 
        DATE_TRUNC('month', data_movimento) as mes,
        codigo_insumo::TEXT,
        descricao_insumo,
        regional,
        SUM(total) / NULLIF(SUM(quantidade), 0) as preco_medio
    FROM view_consolidado_precos
    WHERE codigo_insumo IS NOT NULL
    GROUP BY 1, 2, 3, 4
),
variacao_precos AS (
    SELECT 
        *,
        LAG(preco_medio) OVER (PARTITION BY codigo_insumo, regional ORDER BY mes) as preco_mes_anterior
    FROM preco_medio_mensal
),
calculo_variacao AS (
    SELECT 
        *,
        (preco_medio / NULLIF(preco_mes_anterior, 0)) - 1 as variacao_percentual
    FROM variacao_precos
)
SELECT 
    cv.mes,
    cv.codigo_insumo,
    cv.descricao_insumo,
    cv.regional,
    cv.variacao_percentual * 100 as variacao_percentual, -- Convertido para %
    abc.contribuicao_percentual as peso_cesta,
    abc.classe_abc,
    (cv.variacao_percentual * abc.contribuicao_percentual) * 100 as impacto_inflacao -- Convertido para %
FROM calculo_variacao cv
JOIN view_curva_abc_insumos abc ON cv.codigo_insumo = abc.codigo_insumo::TEXT
ORDER BY cv.mes DESC, impacto_inflacao DESC;
"""

VIEW_INFLACAO_MENSAL = """
CREATE OR REPLACE VIEW view_inflacao_mensal AS
SELECT 
    mes,
    regional,
    SUM(impacto_inflacao) as inflacao_mensal_regional,
    SUM(peso_cesta) as cobertura_cesta 
FROM view_inflacao_por_insumo
GROUP BY mes, regional
ORDER BY mes DESC, regional;
"""

VIEW_INFLACAO_POR_CLASSE_ABC = """
CREATE OR REPLACE VIEW view_inflacao_por_classe_abc AS
SELECT 
    mes,
    regional,
    classe_abc,
    SUM(impacto_inflacao) as inflacao_classe,
    SUM(peso_cesta) as cobertura_classe
FROM view_inflacao_por_insumo
GROUP BY 1, 2, 3
ORDER BY mes DESC, classe_abc;
"""

VIEW_INFLACAO_GLOBAL = """
CREATE OR REPLACE VIEW view_inflacao_global AS
WITH dados_ponderados AS (
    SELECT 
        im.mes,
        im.regional,
        im.inflacao_mensal_regional,
        cr.unidades
    FROM view_inflacao_mensal im
    JOIN config_regionais cr ON im.regional = cr.regional
)
SELECT 
    mes,
    SUM(inflacao_mensal_regional * unidades) / NULLIF(SUM(unidades), 0) as inflacao_global_ponderada,
    SUM(unidades) as total_unidades_base
FROM dados_ponderados
GROUP BY mes
ORDER BY mes DESC;
"""

VIEW_INFLACAO_POR_GRUPO = """
CREATE OR REPLACE VIEW view_inflacao_por_grupo AS
SELECT 
    gi.grupo_de_insumo,
    vpi.mes,
    SUM(vpi.impacto_inflacao) as inflacao_grupo
FROM view_inflacao_por_insumo vpi
JOIN grupo_insumo gi ON vpi.codigo_insumo = gi.codigo_insumo::TEXT
GROUP BY 1, 2
ORDER BY vpi.mes DESC, inflacao_grupo DESC;
"""

VIEW_INFLACAO_POR_FORNECEDOR = """
CREATE OR REPLACE VIEW view_inflacao_por_fornecedor AS
WITH variacao_fornecedor AS (
    SELECT 
        DATE_TRUNC('month', cp.data_movimento) as mes,
        cp.codigo_fornecedor,
        cp.codigo_insumo,
        SUM(cp.total) / NULLIF(SUM(cp.quantidade), 0) as preco_medio
    FROM view_consolidado_precos cp
    WHERE cp.codigo_insumo IS NOT NULL
    GROUP BY 1, 2, 3
),
calculo_variacao AS (
    SELECT 
        *,
        (preco_medio / NULLIF(LAG(preco_medio) OVER (PARTITION BY codigo_fornecedor, codigo_insumo ORDER BY mes), 0)) - 1 as variacao_percentual
    FROM variacao_fornecedor
)
SELECT 
    f.fornecedor,
    cv.mes,
    AVG(cv.variacao_percentual) * 100 as variacao_media_precos -- Convertido para %
FROM calculo_variacao cv
JOIN fornecedores f ON cv.codigo_fornecedor = f.codigo_fornecedor::TEXT
GROUP BY 1, 2
ORDER BY cv.mes DESC, variacao_media_precos DESC;
"""
