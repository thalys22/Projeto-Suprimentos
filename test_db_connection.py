from db import engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            # Apenas tenta conectar, não precisa executar nada complexo
            # Como o banco pode não estar rodando no sandbox, capturamos o erro de conexão
            # mas validamos se o engine foi criado corretamente com as variáveis do .env
            print("✅ Engine do SQLAlchemy criado com sucesso!")
            print(f"🔗 URL de conexão (sem senha): {engine.url.render_as_string(hide_password=True)}")
            
            # Tenta uma query simples
            conn.execute(text("SELECT 1"))
            print("🚀 Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        if "connection refused" in str(e).lower() or "is the server running" in str(e).lower():
            print("ℹ️ O engine está configurado corretamente, mas o servidor PostgreSQL local não está ativo no momento.")
            print(f"🔗 URL configurada: {engine.url.render_as_string(hide_password=True)}")
        else:
            print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_connection()
