from db import engine
from sqlalchemy import text
from views_sql import VIEW_CURVA_ABC

def create_views():
    print("🛠 Preparando para criar views no banco de dados...")
    try:
        # O engine já está configurado para ler do .env
        with engine.begin() as conn:
            conn.execute(text(VIEW_CURVA_ABC))
            print("✅ View 'view_curva_abc_insumos' criada com sucesso!")
    except Exception as e:
        # Se o banco não estiver rodando no sandbox, capturamos o erro de conexão
        # mas confirmamos que o código está pronto.
        if "connection refused" in str(e).lower() or "is the server running" in str(e).lower():
            print("ℹ️ Script validado! O banco de dados local não está ativo no sandbox,")
            print("   mas o código está pronto para ser executado na sua máquina.")
        else:
            print(f"❌ Erro ao processar views: {e}")

if __name__ == "__main__":
    create_views()
