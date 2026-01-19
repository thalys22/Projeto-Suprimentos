import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Opção 1: Usar URL completa do banco (se preferir)
DATABASE_URL = os.getenv("DATABASE_URL")

# Opção 2: Construir a partir de componentes individuais
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "gestao_suprimentos")

    if not DB_PASSWORD:
        raise ValueError("A variável de ambiente DB_PASSWORD não foi definida no arquivo .env")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

engine = create_engine(DATABASE_URL)
