import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not DB_PASSWORD:
  raise ValueError("A variável de ambiente DB_PASSWORD não foi definida")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def test_connection():
    try:
        with engine.connect() as conn:
            print("Engine do SQLAlchemy criado com sucesso.")
            print(f"URL de conexao (sem senha): {engine.url.render_as_string(hide_password=True)}")
            conn.execute(text("SELECT 1"))
            print("Conexao com o banco de dados estabelecida com sucesso.")
    except UnicodeDecodeError:
        print("Falha de autenticacao/encoding ao abrir conexao.")
        print("Verifique DB_USER/DB_PASSWORD/DB_HOST no arquivo .env.")
        print(f"URL configurada: {engine.url.render_as_string(hide_password=True)}")
    except OperationalError as e:
        msg = str(e).lower()
        if "connection refused" in msg or "is the server running" in msg:
            print("Servidor PostgreSQL indisponivel (conexao recusada).")
        elif "could not translate host name" in msg or "name or service not known" in msg:
            print("Host do banco invalido ou sem resolucao DNS.")
        elif "timeout expired" in msg:
            print("Tempo limite de conexao com o banco excedido.")
        else:
            print(f"Falha operacional de conexao: {e}")
        print(f"URL configurada: {engine.url.render_as_string(hide_password=True)}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    test_connection()
    