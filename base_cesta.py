import pandas as pd
from parse_NF import read_and_unmerge_excel, drop_empty_columns_df, normalize_header, split_insumo, clean_df
FILEPATH = "data/baseCesta.xlsx"
SHEET_NAME = "Relatório"

def extract_blocks(rows):
  data = []
  header = None
  
  for row in rows:
    if (row and isinstance(row[0], str) and row[0] == "Insumo"):
      header = normalize_header(row)
      continue
    
    if header and row and isinstance(row[0], str):
      record = dict(zip(header, row))
      data.append(record)
  
  return pd.DataFrame(data)

def del_columns(df):
  return df.loc[:, ~df.columns.str.startswith("None")]

def parse_excel_apropriacoes():
  rows = read_and_unmerge_excel(FILEPATH, SHEET_NAME)
  df = extract_blocks(rows)
  df = drop_empty_columns_df(df)
  df = del_columns(df)
  df = clean_df(df)
  df = split_insumo(df)
  
  return df

if __name__ == "__main__":
  df = parse_excel_apropriacoes()
  output_file = "data/data_frame_cesta.xlsx"
  df.to_excel(output_file, index=False)
  
  print(f"Planilha '{output_file} criada com sucesso!")
  