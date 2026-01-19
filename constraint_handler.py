# constraint_handler.py
"""
Módulo para lidar com Foreign Key Constraints durante inserção de dados.
Implementa estratégias para desabilitar/reabilitar constraints e filtrar dados inválidos.
"""

from sqlalchemy import text
from db import engine
import pandas as pd


def disable_foreign_keys():
    """Desabilita todas as foreign keys no PostgreSQL"""
    try:
        with engine.begin() as conn:
            conn.execute(text("SET session_replication_role = REPLICA;"))
        print("🔓 Foreign keys desabilitadas")
    except Exception as e:
        print(f"⚠️ Erro ao desabilitar FKs: {e}")


def enable_foreign_keys():
    """Reabilita todas as foreign keys no PostgreSQL"""
    try:
        with engine.begin() as conn:
            conn.execute(text("SET session_replication_role = DEFAULT;"))
        print("🔒 Foreign keys reabilitadas")
    except Exception as e:
        print(f"⚠️ Erro ao reabilitar FKs: {e}")


def validate_foreign_key(
    df: pd.DataFrame,
    column_name: str,
    ref_table: str,
    ref_column: str
) -> tuple[pd.DataFrame, int]:
    """
    Valida Foreign Key references e remove registros inválidos
    
    Args:
        df: DataFrame para validar
        column_name: coluna com referência FK
        ref_table: tabela referenciada
        ref_column: coluna na tabela referenciada
        
    Returns:
        (df_valido, qtd_removida)
    """
    try:
        # Obter valores válidos da tabela referenciada
        with engine.connect() as conn:
            query = f"SELECT DISTINCT {ref_column}::TEXT FROM {ref_table} WHERE {ref_column} IS NOT NULL"
            result = conn.execute(text(query))
            valid_ids = set(str(row[0]) for row in result.fetchall())
        
        # Converter coluna para string para comparação
        df_copy = df.copy()
        df_copy[column_name] = df_copy[column_name].astype(str)
        
        # Filtrar registros válidos ou NULL
        mask = (df_copy[column_name].isin(valid_ids)) | (df_copy[column_name] == 'nan')
        df_valido = df[mask]
        
        removidos = len(df) - len(df_valido)
        
        if removidos > 0:
            print(f"⚠️ {removidos} registros removidos por FK inválida em '{column_name}'")
        
        return df_valido, removidos
        
    except Exception as e:
        print(f"⚠️ Erro ao validar FK '{column_name}': {e}")
        return df, 0


def validate_all_foreign_keys(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Valida todas as FKs de uma tabela e remove registros inválidos
    
    Mapeamento de FKs por tabela:
    """
    
    fk_mappings = {
        "nf_movimentos": [
            ("codigo_fornecedor", "fornecedores", "codigo_fornecedor"),
        ],
        "nfse_medicoes": [
            ("codigo_fornecedor", "fornecedores", "codigo_fornecedor"),
        ],
        "base_cesta_apropriacoes": [],
        "solicitacoes": [
            ("codigo_fornecedor", "fornecedores", "codigo_fornecedor"),
        ],
    }
    
    if table_name not in fk_mappings:
        return df
    
    df_valido = df.copy()
    total_removidos = 0
    
    for col_name, ref_table, ref_col in fk_mappings[table_name]:
        if col_name in df_valido.columns:
            df_valido, removidos = validate_foreign_key(df_valido, col_name, ref_table, ref_col)
            total_removidos += removidos
    
    if total_removidos > 0:
        print(f"📊 Total: {total_removidos} registros removidos em '{table_name}'")
    
    return df_valido


if __name__ == "__main__":
    print("Módulo constraint_handler carregado com sucesso")
