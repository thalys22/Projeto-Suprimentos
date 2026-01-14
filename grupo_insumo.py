import pandas as pd
from utils import read_and_unmerge_excel, clean_df, del_columns

SHEET_NAME = "Sheet1"
FILE_PATH = "data/base/grupo_de_insumo.xlsx"

def extract_blocks(rows):
    data = []
    header = None
    seen = set()

    for row in rows:
        if row and isinstance(row[0], str) and row[0] == "codigo_insumo":
            header = row
            continue

        if header and row and isinstance(row[0], int):
            unique_key = tuple(row)
            if unique_key in seen:
                continue
            seen.add(unique_key)
            record = dict(zip(header, row))
            data.append(record)

    return pd.DataFrame(data)

def unmerge_path():
    rows = read_and_unmerge_excel(FILE_PATH, SHEET_NAME)
    df = extract_blocks(rows)
    df = clean_df(df)
    df = del_columns(df)
    df = df.sort_values(by=["codigo_insumo", "indice_grupo", "grupo_de_insumo"]).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = unmerge_path()
    output_file = "data/5-grupo_de_insumo.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Planilha '{output_file}' criada com sucesso!")
