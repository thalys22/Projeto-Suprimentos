import pandas as pd
from openpyxl import load_workbook
from utils import clean_df, split_insumo
from parse_NFSE import split_fornecedor

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
    for col in ["Data do pedido", "Data da solicitação", "Previsão de entrega", "Data entrega na obra"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    return df

def insert_urgencia(df):
    if "Previsão de entrega" in df.columns and "Data da solicitação" in df.columns:
        df["dias"] = (df["Previsão de entrega"] - df["Data da solicitação"]).dt.days
        df["urgencia"] = "Não urgente"
        df.loc[df["dias"] < 25, "urgencia"] = "Urgente"
    return df

def start():
    rows = read_cells(FILE_PATH, SHEET_NAME)
    df = extract_blocks(rows)
    df = df[df["Obra"].astype(str).str.lower().str.contains("obra", na=False)]
    df = converter_data(df)
    df = insert_urgencia(df)
    df = split_insumo(df, column_name="Descrição do insumo")
    
    COLUNAS = [
        "Nº da Solicitação", "Obra", "codigo_insumo", "descricao_insumo",
        "Data da solicitação", "N° do Pedido", "Data do pedido", "Comprador",
        "Cód. Fornecedor", "Previsão de entrega", "Data entrega na obra",
        "N° da Nota fiscal", "Unidade de movimento", "urgencia"
    ]
    df = df[COLUNAS]
    df = df.rename(columns={
        "Nº da Solicitação": "numero_solicitacao",
        "Data da solicitação": "data_solicitacao",
        "Previsão de entrega": "previsao_de_entrega",
        "Cód. Fornecedor": "codigo_fornecedor",
        "Data do pedido": "data_pedido",
        "Data entrega na obra": "data_entrega_na_obra",
        "Obra":"centro_custo"
    })
    return df

if __name__ == "__main__":
    df = start()
    nome_arquivo = 'data/6-urgencias.xlsx'
    df.to_excel(nome_arquivo, index=False)
    print(f"Planilha '{nome_arquivo}' criada com sucesso!")
