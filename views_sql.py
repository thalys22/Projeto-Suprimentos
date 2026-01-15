# views_sql.py

VIEW_CURVA_ABC = """
CREATE OR REPLACE VIEW view_curva_abc_insumos AS
WITH total_geral AS (
    -- Calcula o valor total de todos os insumos na cesta
    SELECT SUM(total) as valor_global
    FROM base_cesta_apropriacoes
),
insumos_agrupados AS (
    -- Agrupa por insumo e soma os valores
    SELECT 
        codigo_insumo,
        descricao_insumo,
        SUM(quantidade) as qtd_total,
        SUM(total) as valor_total_insumo
    FROM base_cesta_apropriacoes
    GROUP BY codigo_insumo, descricao_insumo
),
calculo_contribuicao AS (
    -- Calcula a contribuição percentual de cada insumo
    SELECT 
        ia.*,
        (ia.valor_total_insumo / tg.valor_global) as contribuicao_percentual
    FROM insumos_agrupados ia, total_geral tg
),
calculo_acumulado AS (
    -- Calcula o acumulado ordenado do maior para o menor
    SELECT 
        *,
        SUM(contribuicao_percentual) OVER (ORDER BY contribuicao_percentual DESC) as contribuicao_acumulada
    FROM calculo_contribuicao
)
-- Classifica em A, B ou C
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
    -- Identifica quais insumos em quais obras foram urgentes
    SELECT DISTINCT 
        codigo_insumo, 
        centro_custo 
    FROM solicitacoes 
    WHERE urgencia = 'Urgente'
),
movimentos_filtrados AS (
    -- Consolida NF Movimentos (Insumos)
    SELECT 
        nf.data_movimento,
        nf.codigo_insumo,
        nf.descricao_insumo,
        nf.quantidade,
        nf.preco_unitario,
        nf.total,
        nf.centro_custo,
        nf.regional,
        'NF' as origem
    FROM nf_movimentos nf
    LEFT JOIN solicitacoes_urgentes su ON nf.codigo_insumo = su.codigo_insumo AND nf.centro_custo = su.centro_custo
    WHERE su.codigo_insumo IS NULL -- Filtra apenas os NÃO urgentes
    
    UNION ALL
    
    -- Consolida NFSE Medições (Serviços/Insumos)
    SELECT 
        se.data_movimento,
        NULL as codigo_insumo, -- NFSE geralmente não tem código de insumo direto
        se.descricao_insumo,
        se.quantidade,
        se.preco_unitario,
        se.total,
        se.centro_custo,
        se.regional,
        'NFSE' as origem
    FROM nfse_medicoes se
    -- Nota: NFSE geralmente não passa pelo fluxo de solicitações urgentes da mesma forma, 
    -- mas se passar, o filtro abaixo pode ser adaptado.
)
SELECT * FROM movimentos_filtrados;
"""

VIEW_INFLACAO_MENSAL = """
CREATE OR REPLACE VIEW view_inflacao_mensal AS
WITH preco_medio_mensal AS (
    -- Calcula o preço médio de cada insumo por mês e regional
    SELECT 
        DATE_TRUNC('month', data_movimento) as mes,
        codigo_insumo,
        regional,
        SUM(total) / NULLIF(SUM(quantidade), 0) as preco_medio
    FROM view_consolidado_precos
    WHERE codigo_insumo IS NOT NULL
    GROUP BY 1, 2, 3
),
variacao_precos AS (
    -- Calcula a variação em relação ao mês anterior (Lag)
    SELECT 
        *,
        LAG(preco_medio) OVER (PARTITION BY codigo_insumo, regional ORDER BY mes) as preco_mes_anterior
    FROM preco_medio_mensal
),
calculo_variacao AS (
    -- Calcula o percentual de variação
    SELECT 
        *,
        (preco_medio / NULLIF(preco_mes_anterior, 0)) - 1 as variacao_percentual
    FROM variacao_precos
),
inflacao_ponderada AS (
    -- Cruza com a Curva ABC para pegar os pesos (contribuição_percentual)
    SELECT 
        cv.*,
        abc.contribuicao_percentual as peso_cesta,
        cv.variacao_percentual * abc.contribuicao_percentual as variacao_ponderada
    FROM calculo_variacao cv
    JOIN view_curva_abc_insumos abc ON cv.codigo_insumo = abc.codigo_insumo
)
-- Resultado Final: Inflação por Mês e Regional
SELECT 
    mes,
    regional,
    SUM(variacao_ponderada) as inflacao_mensal_regional,
    -- Soma de todos os pesos presentes no mês para normalizar se necessário
    SUM(peso_cesta) as cobertura_cesta 
FROM inflacao_ponderada
GROUP BY mes, regional
ORDER BY mes DESC, regional;
"""

VIEW_INFLACAO_GLOBAL = """
CREATE OR REPLACE VIEW view_inflacao_global AS
WITH dados_ponderados AS (
    -- Junta a inflação mensal regional com a configuração de unidades
    SELECT 
        im.mes,
        im.regional,
        im.inflacao_mensal_regional,
        cr.unidades
    FROM view_inflacao_mensal im
    JOIN config_regionais cr ON im.regional = cr.regional
)
-- Aplica a fórmula: ((Inf_SE * Un_SE) + (Inf_BA * Un_BA)) / Total_Unidades
SELECT 
    mes,
    SUM(inflacao_mensal_regional * unidades) / NULLIF(SUM(unidades), 0) as inflacao_global_ponderada,
    SUM(unidades) as total_unidades_base
FROM dados_ponderados
GROUP BY mes
ORDER BY mes DESC;
"""
