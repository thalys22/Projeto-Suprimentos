import insert_dataframes


def main():
    print("Inserindo dados no banco...")
    insert_dataframes.insert_all()
    print("✔ Pipeline executado com sucesso")


if __name__ == "__main__":
    main()
