from db import engine

from parse_NF import parse_excel_movimentos
from parse_NFSE import parse_excel_medicoes
from base_cesta import parse_excel_apropriacoes
from solicitacoes_urgentes import start as parse_solicitacoes
from fornecedor import unmerge_path as parse_fornecedores


def insert_fornecedores():
    df = parse_fornecedores()
    df = df.drop_duplicates(subset=["codigo"])
    df.to_sql("fornecedores", engine, if_exists="append", index=False)
    print("✔ fornecedores")


def insert_nf_movimentos():
    df = parse_excel_movimentos()
    df.to_sql("nf_movimentos", engine, if_exists="append", index=False)
    print("✔ nf_movimentos")


def insert_nfse_medicoes():
    df = parse_excel_medicoes()
    df.to_sql("nfse_medicoes", engine, if_exists="append", index=False)
    print("✔ nfse_medicoes")


def insert_cesta():
    df = parse_excel_apropriacoes()
    df.to_sql("cesta_apropriacoes", engine, if_exists="append", index=False)
    print("✔ cesta_apropriacoes")


def insert_solicitacoes():
    df = parse_solicitacoes()
    df.to_sql("solicitacoes", engine, if_exists="append", index=False)
    print("✔ solicitacoes")


def insert_all():
    print("🚀 Iniciando carga...\n")

    insert_fornecedores()
    insert_nf_movimentos()
    insert_nfse_medicoes()
    insert_cesta()
    insert_solicitacoes()

    print("\n✅ Carga finalizada com sucesso!")


if __name__ == "__main__":
    insert_all()
