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
