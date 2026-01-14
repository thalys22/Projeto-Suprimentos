import pandas as pd
from utils import (
    read_and_unmerge_excel, 
    normalize_header, 
    drop_empty_columns_df, 
    create_regional, 
    clean_df
)

FILEPATH = "data/base/medicoes.xlsx"
SHEET_NAME = "Relatório"

def split_fornecedor(df):
    if "fornecedor" not in df.columns:
        return df
    
    split_data = df["fornecedor"].astype(str).str.split(" - ", n=1, expand=True)
    df["codigo_fornecedor"] = split_data[0].str.strip()
    if split_data.shape[1] > 1:
        df["descricao_fornecedor"] = split_data[1].str.strip()
    else:
        df["descricao_fornecedor"] = None
    
    df = df.drop(columns=["fornecedor"])
    return df

def extract_blocks(rows):
    data = []
    current_date = None
    current_cc = None
    header = None
    supplier = None
    
    for row in rows:
        if row and isinstance(row[0], str) and row[0] == "Obra":
            current_value = row[2]
            if (isinstance(current_value, str) and "obra" in current_value.lower() and not "gerencia" in current_value.lower()):
                current_cc = current_value
            
        if row and any(isinstance(cell, str) and cell.strip() == "Data da medição" for cell in row):
            current_date = pd.to_datetime(row[16], dayfirst=True)
            
        if row and any(isinstance(cell, str) and cell.strip() == "Fornecedor" for cell in row):
            supplier = row[16]
        
        if row and isinstance(row[0], str) and row[0] == "Referência":
            header = normalize_header(row)
            continue  
        
        if (header and row and isinstance(row[0], str) and row[0].startswith("00") and current_cc):
            record = dict(zip(header, row))
            record["data_movimento"] = current_date
            record["centro_custo"] = current_cc
            record["fornecedor"] = supplier
            data.append(record)
    
    return pd.DataFrame(data)

def parse_excel_medicoes():
    rows = read_and_unmerge_excel(FILEPATH, SHEET_NAME)
    df = extract_blocks(rows)
    df = drop_empty_columns_df(df)
    df = split_fornecedor(df)
    df = create_regional(df)
    df = clean_df(df)
    
    COLUNAS_NFSE = [
        "descricao", "un", "medida", "preco_unitario", 
        "medicao", "data_movimento", "centro_custo", 
        "codigo_fornecedor", "regional"
    ]

    df = df[COLUNAS_NFSE]
    df = df.rename(columns={
        "descricao": "descricao_insumo",
        "medida": "quantidade",
        "medicao": "total"
    })

    return df

if __name__ == "__main__":
    df = parse_excel_medicoes()
    output_file = "data/2-data_frame_medicoes.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Planilha '{output_file} criada com sucesso!")
