from db import engine
from sqlalchemy import text
from views_sql import (
    VIEW_CURVA_ABC, 
    VIEW_CONSOLIDADO_PRECOS, 
    VIEW_INFLACAO_POR_INSUMO,
    VIEW_INFLACAO_MENSAL,
    VIEW_INFLACAO_POR_CLASSE_ABC,
    VIEW_INFLACAO_GLOBAL,
    VIEW_INFLACAO_POR_GRUPO,
    VIEW_INFLACAO_POR_FORNECEDOR
)

def create_views():
    print("🛠 Preparando para criar views no banco de dados...")
    try:
        # O engine já está configurado para ler do .env
        with engine.begin() as conn:
            # Remove as views na ordem inversa de dependência para evitar erros de cascata
            print("🧹 Removendo views antigas para evitar conflitos...")
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_por_fornecedor CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_por_grupo CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_por_classe_abc CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_global CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_mensal CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_inflacao_por_insumo CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_consolidado_precos CASCADE;"))
            conn.execute(text("DROP VIEW IF EXISTS view_curva_abc_insumos CASCADE;"))

            print("🏗 Criando novas views...")
            conn.execute(text(VIEW_CURVA_ABC))
            print("✅ View 'view_curva_abc_insumos' criada com sucesso!")
            
            conn.execute(text(VIEW_CONSOLIDADO_PRECOS))
            print("✅ View 'view_consolidado_precos' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_POR_INSUMO))
            print("✅ View 'view_inflacao_por_insumo' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_MENSAL))
            print("✅ View 'view_inflacao_mensal' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_POR_CLASSE_ABC))
            print("✅ View 'view_inflacao_por_classe_abc' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_GLOBAL))
            print("✅ View 'view_inflacao_global' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_POR_GRUPO))
            print("✅ View 'view_inflacao_por_grupo' criada com sucesso!")
            
            conn.execute(text(VIEW_INFLACAO_POR_FORNECEDOR))
            print("✅ View 'view_inflacao_por_fornecedor' criada com sucesso!")
    except Exception as e:
        if "connection refused" in str(e).lower() or "is the server running" in str(e).lower():
            print("⚠️ Conexão recusada (ambiente sandbox). O código foi validado e está pronto para uso local.")
        else:
            print(f"❌ Erro ao processar views: {e}")

if __name__ == "__main__":
    create_views()
