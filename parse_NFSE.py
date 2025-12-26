import pandas as pd
from openpyxl import load_workbook
from parse_NF import read_and_unmerge_excel, normalize_header

FILEPATH = "data/medicoes.xlsx"
SHEET_NAME = "Relatório"


def extract_blocks(rows):
  data = []
  current_date = None
  current_cc = None
  header = None
  supplier = None
  header = None
  
  for row in rows:
    if row and isinstance(row[0], str) and row[0] == "Obra":
      current_cc = row[2]
      
    if row and any(isinstance(cell, str) and cell.strip() == "Data da medição" for cell in row):
      current_date = pd.to_datetime(row[16], dayfirst=True)
      
    if row and any(isinstance(cell, str) and cell.strip() == "Fornecedor" for cell in row):
      supplier = row[16]
    
    if row and isinstance(row[0], str) and row[0] == "Referência":
      header = normalize_header(row)
      continue  
    

    if (header and row and isinstance(row[0], str) and row[0].startswith("00")):
      record = dict(zip(header, row))
      record["data_movimento"] = current_date
      record["centro_custo"] = current_cc
      record["fornecedor"] = supplier
      data.append(record)
  
  return pd.DataFrame(data)

def parse_excel_medicoes():
  rows = read_and_unmerge_excel(FILEPATH, SHEET_NAME)
  df = extract_blocks(rows)
  return df

if __name__ == "__main__":
  df = parse_excel_medicoes()
  output_file = "data/data_frame_medicoes.xlsx"
  df.to_excel(output_file, index=False)
  
  print(f"Planilha '{output_file} criada com sucesso!")
  
  
