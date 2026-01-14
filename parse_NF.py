import pandas as pd
from utils import (
    read_and_unmerge_excel, 
    normalize_header, 
    clean_df, 
    drop_empty_columns_df, 
    create_regional, 
    split_insumo
)

FILE_PATH = "data/base/notasFiscais.xlsx"
SHEET_NAME = "Relatório"

def extract_blocks(rows):
    data = []
    current_date = None
    current_cc = None
    header = None
    
    for row in rows:
        if (row and isinstance(row[0], str) and "Centro de custo" in row[0]):
            cc_value = row[3]
            if (isinstance(cc_value, str) and "obra" in cc_value.lower()):
                current_cc = cc_value
            
        if row and row[0] == "Data do movimento":
            current_date = pd.to_datetime(row[3], dayfirst=True)
        
        if row and row[0] == "Movimento":
            header = normalize_header(row)
            continue
        
        if (header and row and isinstance(row[0], str) and row[0].startswith("NF")) and current_cc:
            record = dict(zip(header, row))
            record["data_movimento"] = current_date
            record["centro_custo"] = current_cc
            data.append(record)
            
    return pd.DataFrame(data)

def rename_columns(df):
    return df.rename(columns={
        "forn": "fornecedor",
        "histórico_da_operação": "historico_operacao",
        "quantidade": "quantidade",
        "quantidade_2": "quantidade_unidade_basica",
        "unid": "unidade",
        "unid_2": "unidade_basica",
        "preço_unitário": "preco_unitario",
        "preço_unitário_2": "preco_unitario_unidade_basica",
        "total": "total",
        "total_2": "total_unidade_basica",          
    })

def clean_units(df):
    for col in ["unidade", "unidade_basica"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
    return df

def split_movimento(df):
    if "movimento" in df.columns:
        df["movimento"] = df["movimento"].astype(str).str.split("-", n=1).str[0]
    return df

def parse_excel_movimentos():
    rows = read_and_unmerge_excel(FILE_PATH, SHEET_NAME)
    df = extract_blocks(rows)
    df = drop_empty_columns_df(df)
    df = clean_df(df)
    df = rename_columns(df)
    df = clean_units(df)
    df = split_insumo(df)
    df = create_regional(df)
    df = split_movimento(df)
    
    COLUNAS_NF = [
        "movimento", "fornecedor", "quantidade", "unidade", 
        "preco_unitario", "total", "data_movimento", 
        "centro_custo", "codigo_insumo", "descricao_insumo", "regional"
    ]
    
    df = df[COLUNAS_NF]
    df = df.rename(columns={"fornecedor": "codigo_fornecedor", "unidade": "un"})
    return df 

if __name__ == "__main__":
    df = parse_excel_movimentos()
    nome_arquivo = 'data/1-data_frame_NF.xlsx'
    df.to_excel(nome_arquivo, index=False)
    print(f"Planilha '{nome_arquivo}' criada com sucesso!")
