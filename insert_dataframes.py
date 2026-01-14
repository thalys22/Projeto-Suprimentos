# insert_dataframes.py

from db import engine
from deduplication import filter_new_rows

from parse_NF import parse_excel_movimentos
from parse_NFSE import parse_excel_medicoes
from base_cesta import parse_excel_apropriacoes
from solicitacoes_urgentes import start as parse_solicitacoes
from fornecedor import unmerge_path as parse_fornecedores
from grupo_insumo import unmerge_path as parse_grupo_insumo


# =========================================================
# CONFIGURAÇÃO CENTRAL DAS TABELAS
# =========================================================
# Cada entrada define:
# - parser: função que retorna o DataFrame JÁ NORMALIZADO
# - keys: chave natural (business key) para deduplicação
# =========================================================

TABLES_CONFIG = {
    "fornecedores": {
        "parser": parse_fornecedores,
        "keys": ["codigo_fornecedor"],
    },
    "grupo_insumo": {
        "parser": parse_grupo_insumo,
        "keys": ["codigo_insumo"],
    },
    "nf_movimentos": {
        "parser": parse_excel_movimentos,
        "keys": ["movimento", "codigo_insumo", "centro_custo"],
    },
    "nfse_medicoes": {
        "parser": parse_excel_medicoes,
        "keys": ["descricao_insumo", "data_movimento", "centro_custo"],
    },
    "base_cesta_apropriacoes": {
        "parser": parse_excel_apropriacoes,
        "keys": ["codigo_insumo", "centro_custo"],
    },
    "solicitacoes": {
        "parser": parse_solicitacoes,
        "keys": ["numero_solicitacao", "codigo_insumo"],
    },
}


# =========================================================
# INSERÇÃO GENÉRICA POR TABELA
# =========================================================
def insert_table(table_name: str, config: dict):
    print(f"\n📥 Processando tabela: {table_name}")

    # 1️⃣ Executa o parser
    df = config["parser"]()

    if df is None or df.empty:
        print(f"⚠ {table_name}: DataFrame vazio — nada a inserir")
        return

    # 2️⃣ Validação preventiva das colunas-chave
    missing = set(config["keys"]) - set(df.columns)
    if missing:
        raise ValueError(
            f"[{table_name}] Colunas de chave ausentes no DataFrame: {missing}"
        )

    # 3️⃣ Deduplicação contra o banco
    df_new, inserted, discarded = filter_new_rows(
        df=df,
        engine=engine,
        table_name=table_name,
        key_columns=config["keys"],
    )

    # 4️⃣ Insert apenas se houver dados novos
    if df_new.empty:
        print(f"⚠ {table_name}: nenhuma linha nova")
        return

    df_new.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
    )

    # 5️⃣ Log final
    print(
        f"✔ {table_name}: inseridas={inserted} | descartadas={discarded}"
    )


# =========================================================
# PIPELINE COMPLETO
# =========================================================
def insert_all():
    for table_name, config in TABLES_CONFIG.items():
        insert_table(table_name, config)
