import pandas as pd
from openpyxl import load_workbook

FILE_PATH = "data/base/solicitacoesUrgentes.xlsx"
SHEET_NAME = "Sheet1"

def read_cells(file_path, sheet_name):
  wb = load_workbook(file_path, data_only=True)
  ws = wb[sheet_name]
  rows = []
  for row in ws.iter_rows(values_only=True):
    rows.append(list(row))
  return rows

def extract_blocks(rows):
    data = []
    header = None

    for row in rows:
        if row and isinstance(row[0], str) and row[0] == "Nº da Solicitação":
            header = row
            continue

        if header and row and isinstance(row[0], int):
            record = dict(zip(header, row))
            data.append(record)

    return pd.DataFrame(data)


def converter_data(df):
    df["Data para chegada à obra"] = pd.to_datetime(
        df["Data para chegada à obra"],
        dayfirst=True,
        errors="coerce"
    )

    df["Data da solicitação"] = pd.to_datetime(
        df["Data da solicitação"],
        dayfirst=True,
        errors="coerce"
    )

    return df


def insert_urgencia(df):
    df["dias"] = (
        df["Data para chegada à obra"] - df["Data da solicitação"]
    ).dt.days

    df["urgencia"] = "Não urgente"

    df.loc[df["dias"] < 25, "urgencia"] = "Urgente"

    return df

    
def start():
    rows = read_cells(FILE_PATH, SHEET_NAME)
    df = extract_blocks(rows)
    df = df[df["Obra"].astype(str).str.lower().str.contains("obra", na=False)]
    df = converter_data(df)
    df = insert_urgencia(df)
    return df


if __name__ == "__main__":
  df = start()
  nome_arquivo = 'data/4-urgencias.xlsx'
  df.to_excel(nome_arquivo, index=False)
  print(f"Planilha '{nome_arquivo}' criada com sucesso!")
  
