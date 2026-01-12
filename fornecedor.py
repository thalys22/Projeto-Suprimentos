
import pandas as pd
from parse_NF import read_and_unmerge_excel, clean_df
from base_cesta import del_columns

SHEET_NAME = "Relatório"
FILE_PATH = "data/base/fornecedores.xlsx"

def extract_blocks(rows):
    data = []
    header = None
    seen = set()  

    for row in rows:
        if row and isinstance(row[0], str) and row[0] == "Código":
            header = row
            continue

        if header and row and isinstance(row[0], int):
            codigo = row[0]
            fornecedor = row[1]
            unique_key = (codigo, fornecedor)
            
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
  df = df[["codigo", "fornecedor"]]
  df = df.sort_values(by=["codigo", "fornecedor"]).reset_index(drop=True)
  
  return df

if __name__ == "__main__":
  df_fornecedores = unmerge_path()
  output_file = "data/4-fornecedores.xlsx"
  df_fornecedores.to_excel(output_file, index=False)
  
  print(f"Planilha '{output_file}' criada com sucesso!")
    
