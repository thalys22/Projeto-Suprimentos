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
WITH preco_mediano_mensal AS (
    -- Calcula a mediana do preço unitário por mês, insumo e regional
    SELECT 
        DATE_TRUNC('month', data_movimento) as mes,
        codigo_insumo::TEXT,
        descricao_insumo,
        regional,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco_unitario) as preco_mediano
    FROM view_consolidado_precos
    WHERE codigo_insumo IS NOT NULL
    GROUP BY 1, 2, 3, 4
),
variacao_precos AS (
    SELECT 
        *,
        LAG(preco_mediano) OVER (PARTITION BY codigo_insumo, regional ORDER BY mes) as preco_mes_anterior
    FROM preco_mediano_mensal
),
calculo_variacao AS (
    SELECT 
        *,
        (preco_mediano / NULLIF(preco_mes_anterior, 0)) - 1 as variacao_percentual_bruta
    FROM variacao_precos
),
filtro_outliers AS (
    -- Aplica o filtro de 15% de variação mensal
    SELECT 
        *
    FROM calculo_variacao
    WHERE ABS(variacao_percentual_bruta) <= 0.15 OR preco_mes_anterior IS NULL
)
SELECT 
    fo.mes,
    fo.codigo_insumo,
    fo.descricao_insumo,
    fo.regional,
    fo.variacao_percentual_bruta * 100 as variacao_percentual,
    abc.contribuicao_percentual as peso_cesta,
    abc.classe_abc,
    (fo.variacao_percentual_bruta * abc.contribuicao_percentual) * 100 as impacto_inflacao
FROM filtro_outliers fo
JOIN view_curva_abc_insumos abc ON fo.codigo_insumo = abc.codigo_insumo::TEXT;
"""

VIEW_INFLACAO_MENSAL = """
CREATE OR REPLACE VIEW view_inflacao_mensal AS
WITH mensal AS (
    SELECT 
        mes,
        regional,
        SUM(impacto_inflacao) as inflacao_mensal_regional,
        SUM(peso_cesta) as cobertura_cesta 
    FROM view_inflacao_por_insumo
    GROUP BY mes, regional
)
SELECT 
    *,
    -- Inflação Acumulada Anual (reinicia em Janeiro)
    SUM(inflacao_mensal_regional) OVER (PARTITION BY regional, DATE_TRUNC('year', mes) ORDER BY mes) as inflacao_acumulada_ano
FROM mensal
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
),
global_mensal AS (
    SELECT 
        mes,
        SUM(inflacao_mensal_regional * unidades) / NULLIF(SUM(unidades), 0) as inflacao_global_ponderada,
        SUM(unidades) as total_unidades_base
    FROM dados_ponderados
    GROUP BY mes
)
SELECT 
    *,
    SUM(inflacao_global_ponderada) OVER (PARTITION BY DATE_TRUNC('year', mes) ORDER BY mes) as inflacao_global_acumulada_ano
FROM global_mensal
ORDER BY mes DESC;
"""

VIEW_INFLACAO_POR_GRUPO = """
CREATE OR REPLACE VIEW view_inflacao_por_grupo AS
SELECT 
    gi.grupo_de_insumo,
    vpi.mes,
    vpi.regional,
    SUM(vpi.impacto_inflacao) as inflacao_grupo
FROM view_inflacao_por_insumo vpi
JOIN grupo_insumo gi ON vpi.codigo_insumo = gi.codigo_insumo::TEXT
GROUP BY 1, 2, 3
ORDER BY vpi.mes DESC, inflacao_grupo DESC;
"""

VIEW_INFLACAO_POR_FORNECEDOR = """
CREATE OR REPLACE VIEW view_inflacao_por_fornecedor AS
WITH variacao_fornecedor AS (
    SELECT 
        DATE_TRUNC('month', cp.data_movimento) as mes,
        cp.codigo_fornecedor,
        cp.codigo_insumo,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco_unitario) as preco_mediano
    FROM view_consolidado_precos cp
    WHERE cp.codigo_insumo IS NOT NULL
    GROUP BY 1, 2, 3
),
calculo_variacao AS (
    SELECT 
        *,
        (preco_mediano / NULLIF(LAG(preco_mediano) OVER (PARTITION BY codigo_fornecedor, codigo_insumo ORDER BY mes), 0)) - 1 as variacao_percentual
    FROM variacao_fornecedor
)
SELECT 
    f.fornecedor,
    cv.mes,
    AVG(cv.variacao_percentual) * 100 as variacao_media_precos
FROM calculo_variacao cv
JOIN fornecedores f ON cv.codigo_fornecedor = f.codigo_fornecedor::TEXT
GROUP BY 1, 2
ORDER BY cv.mes DESC, variacao_media_precos DESC;
"""
