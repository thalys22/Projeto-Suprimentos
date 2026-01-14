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
