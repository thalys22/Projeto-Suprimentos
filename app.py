"""
Arquivo principal do projeto.
Executa:
1. Criação das tabelas
2. Carga de todos os dataframes no banco
"""

from create_tables import engine  # força import do engine
import create_tables
import insert_dataframes


def main():
    print("🚀 Iniciando aplicação...\n")

    print("📦 Criando tabelas...")
    create_tables  # apenas importar já executa o script
    print("✔ Tabelas prontas\n")

    print("📊 Inserindo dados...")
    insert_dataframes.insert_all()

    print("\n🎉 Processo finalizado com sucesso!")


if __name__ == "__main__":
    main()
