import pandas as pd
from pathlib import Path

from parse_NF import (
    read_and_unmerge_excel,
    drop_empty_columns_df,
    normalize_header,
    split_insumo,
    clean_df
)

BASE_DIR = Path("data/base/baseCesta")
SHEET_NAME = "Relatório"


def extract_blocks(rows):
    data = []
    header = None

    for row in rows:

        if row and isinstance(row[0], str) and row[0] == "Insumo":
            header = normalize_header(row)
            continue

        if (
            header
            and row
            and isinstance(row[0], str)
            and not ("fat. direto" in row[0].lower() or "fat direto" in row[0].lower())
        ):
            record = dict(zip(header, row))
            data.append(record)

    return pd.DataFrame(data)


def del_columns(df):
    return df.loc[:, ~df.columns.str.startswith("None")]


def drop_percent_columns(df):
    return df.loc[:, ~df.columns.str.contains(r"part|acum", case=False, regex=True)]


def create_regional(df):
  if "centro_custo" not in df.columns:
    return df
  split_data = df["centro_custo"].astype(str).str.extract(r"^([^-]+)")
  df["regional"] = split_data[0].str.strip()
  df.loc[df["regional"].str.lower().str.contains("mangabeiras|vista aruana", na=False), "regional"] = "SE"
  return df

def process_single_file(file_path: Path) -> pd.DataFrame:
    rows = read_and_unmerge_excel(file_path, SHEET_NAME)

    df = extract_blocks(rows)
    df = drop_empty_columns_df(df)
    df = del_columns(df)
    df = clean_df(df)
    df = drop_percent_columns(df)
    df = split_insumo(df)
    df = df.iloc[:-3]
    df["centro_custo"] = file_path.stem
    df = create_regional(df)

    return df


def parse_excel_apropriacoes():
    all_dfs = []

    for file_path in BASE_DIR.glob("*.xlsx"):
        print(f"Processando: {file_path.name}")
        df_file = process_single_file(file_path)
        all_dfs.append(df_file)

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)


if __name__ == "__main__":
    df_final = parse_excel_apropriacoes()

    output_file = "data/3-data_frame_cesta_consolidado.xlsx"
    df_final.to_excel(output_file, index=False)

    print(f"Planilha '{output_file}' criada com sucesso!")
