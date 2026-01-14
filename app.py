# app.py
import insert_dataframes


def main():
    print("🚀 Iniciando pipeline de carga...")
    insert_dataframes.insert_all()
    print("\n✅ Pipeline finalizado com sucesso")


if __name__ == "__main__":
    main()
