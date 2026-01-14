import pandas as pd
from sqlalchemy import text


def table_exists(engine, table_name: str) -> bool:
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table
        )
    """
    with engine.begin() as conn:
        return conn.execute(text(query), {"table": table_name}).scalar()


def filter_new_rows(
    df: pd.DataFrame,
    engine,
    table_name: str,
    key_columns: list[str],
):
    """
    Remove do DataFrame as linhas que já existem no banco
    com base nas colunas-chave (chave natural).
    """

    if df.empty:
        return df, 0, 0

    # 🔹 Se a tabela NÃO existe, tudo é novo
    if not table_exists(engine, table_name):
        return df.copy(), len(df), 0

    cols_sql = ", ".join(key_columns)
    query = f"SELECT {cols_sql} FROM {table_name}"

    try:
        existing_df = pd.read_sql(query, engine)
    except Exception:
        # fallback de segurança
        return df.copy(), len(df), 0

    if existing_df.empty:
        return df.copy(), len(df), 0

    # Cria chave composta
    df["_key"] = df[key_columns].astype(str).agg("|".join, axis=1)
    existing_df["_key"] = (
        existing_df[key_columns].astype(str).agg("|".join, axis=1)
    )

    existing_keys = set(existing_df["_key"])

    df_new = df.loc[~df["_key"].isin(existing_keys)].drop(columns="_key")

    inserted = len(df_new)
    discarded = len(df) - inserted

    return df_new, inserted, discarded
