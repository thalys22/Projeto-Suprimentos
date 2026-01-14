# insert_dataframes.py
from db import engine

from parse_NF import parse_excel_movimentos
from parse_NFSE import parse_excel_medicoes
from base_cesta import parse_excel_apropriacoes
from solicitacoes_urgentes import start as parse_solicitacoes
from fornecedor import unmerge_path as parse_fornecedores
from grupo_insumo import unmerge_path as parse_grupo_insumo


def insert_nf_movimentos():
    df = parse_excel_movimentos()
    df.to_sql("nf_movimentos", engine, if_exists="append", index=False)


def insert_nfse_medicoes():
    df = parse_excel_medicoes()
    df.to_sql("nfse_medicoes", engine, if_exists="append", index=False)


def insert_base_cesta():
    df = parse_excel_apropriacoes()
    df.to_sql("base_cesta_apropriacoes", engine, if_exists="append", index=False)


def insert_solicitacoes():
    df = parse_solicitacoes()

    df = df.rename(columns={
        "Nº da Solicitação": "numero_solicitacao",
        "Cód. Insumo": "codigo_insumo",
        "Descrição do insumo": "descricao_insumo",
        "Data da solicitação": "data_solicitacao",
        "Data para chegada à obra": "data_chegada",
        "Cód. Fornecedor": "codigo_fornecedor",
    })

    df.to_sql("solicitacoes", engine, if_exists="append", index=False)


def insert_fornecedores():
    df = parse_fornecedores()
    df.to_sql("fornecedores", engine, if_exists="append", index=False)


def insert_grupo_insumo():
    df = parse_grupo_insumo()
    df.to_sql("grupo_insumo", engine, if_exists="append", index=False)


def insert_all():
    insert_fornecedores()
    print("Dados de fornecedores inseridos com sucesso...")
    insert_grupo_insumo()
    print("Dados de Grupos de insumo inseridos com sucesso...")
    insert_nf_movimentos()
    print("Dados de Notas fiscais inseridos com sucesso...")
    insert_nfse_medicoes()
    print("Dados de Notas de Serviço inseridos com sucesso...")
    insert_base_cesta()
    print("Dados da base da cesta inseridos com sucesso...")
    insert_solicitacoes()
    print("Dados de tipo de solicitações inseridos com sucesso...")
