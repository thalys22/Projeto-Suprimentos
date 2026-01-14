  
import pandas as pd


def filter_new_rows(
    df: pd.DataFrame,
    engine,
    table_name: str,
    key_columns: list[str]
):
    """
    Remove do DataFrame as linhas que já existem no banco
    com base nas colunas-chave (chave natural).
    """

    if df.empty:
        return df, 0, 0

    cols_sql = ", ".join(key_columns)
    query = f"SELECT {cols_sql} FROM {table_name}"

    existing_df = pd.read_sql(query, engine)

    if existing_df.empty:
        return df.copy(), len(df), 0

    df["_key"] = df[key_columns].astype(str).agg("|".join, axis=1)
    existing_df["_key"] = (
        existing_df[key_columns].astype(str).agg("|".join, axis=1)
    )

    existing_keys = set(existing_df["_key"])

    is_new = ~df["_key"].isin(existing_keys)
    df_new = df.loc[is_new].drop(columns="_key")

    inserted = df_new.shape[0]
    discarded = df.shape[0] - inserted

    return df_new, inserted, discarded
