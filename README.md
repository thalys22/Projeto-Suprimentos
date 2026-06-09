# 📦 Projeto Suprimentos

Pipeline de ingestão de dados para a área de suprimentos, desenvolvido em Python. O projeto realiza o parsing de arquivos Excel contendo Notas Fiscais (NF), Notas Fiscais de Serviço (NF-SE), base de cesta de apropriações e solicitações urgentes, carregando todos os dados em um banco de dados PostgreSQL estruturado.

-----

## 🗂️ Estrutura do Projeto

```
Projeto-Suprimentos/
├── app.py                    # Ponto de entrada — executa o pipeline completo
├── db.py                     # Configuração da conexão com o banco (SQLAlchemy + dotenv)
├── models.py                 # Criação das tabelas no banco de dados
├── insert_dataframes.py      # Orquestra a inserção de todos os DataFrames
├── parse_NF.py               # Parser das Notas Fiscais de movimentação
├── parse_NFSE.py             # Parser das Notas Fiscais de Serviço (medições)
├── base_cesta.py             # Parser da base de cesta de apropriações
├── solicitacoes_urgentes.py  # Parser das solicitações urgentes
├── fornecedor.py             # Parser da tabela de fornecedores
├── grupo_insumo.py           # Parser da tabela de grupos de insumo
└── .env                      # Variáveis de ambiente (não versionado)
```

-----

## 🗄️ Modelo de Dados

O banco é organizado em tabelas de **dimensão** e tabelas de **fato**:

**Dimensões**

- `fornecedores` — cadastro de fornecedores
- `grupo_insumo` — grupos e categorias de insumos

**Fatos**

- `nf_movimentos` — movimentações de Notas Fiscais de produtos
- `nfse_medicoes` — medições de Notas Fiscais de Serviço
- `cesta_apropriacoes` — base da cesta de apropriações por insumo
- `solicitacoes` — solicitações de compra com datas e status de urgência

-----

## ⚙️ Pré-requisitos

- Python 3.10+
- PostgreSQL em execução e acessível
- Dependências Python:

```bash
pip install sqlalchemy psycopg2-binary pandas python-dotenv openpyxl
```

-----

## 🔧 Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nome_do_banco
```

-----

## 🚀 Como Executar

**1. Criar as tabelas no banco:**

```bash
python models.py
```

**2. Executar o pipeline completo de ingestão:**

```bash
python app.py
```

O pipeline seguirá a ordem:

1. Fornecedores
1. Grupos de insumo
1. Notas Fiscais (NF)
1. Notas Fiscais de Serviço (NF-SE)
1. Base da cesta de apropriações
1. Solicitações urgentes

**3. Testar a conexão com o banco (opcional):**

```bash
python db.py
```

-----

## 🧩 Descrição dos Módulos

|Arquivo                   |Responsabilidade                                                       |
|--------------------------|-----------------------------------------------------------------------|
|`app.py`                  |Ponto de entrada que chama `insert_all()`                              |
|`db.py`                   |Cria o engine SQLAlchemy a partir do `.env` e testa a conexão          |
|`models.py`               |Executa o DDL de criação das tabelas via `CREATE TABLE IF NOT EXISTS`  |
|`insert_dataframes.py`    |Chama cada parser e insere o DataFrame resultante no banco com `to_sql`|
|`parse_NF.py`             |Lê e trata o Excel de movimentações de NF                              |
|`parse_NFSE.py`           |Lê e trata o Excel de medições de NF-SE                                |
|`base_cesta.py`           |Lê e trata o Excel da base de cesta de apropriações                    |
|`solicitacoes_urgentes.py`|Lê e trata o Excel de solicitações urgentes                            |
|`fornecedor.py`           |Lê e desmerge a planilha de fornecedores                               |
|`grupo_insumo.py`         |Lê e desmerge a planilha de grupos de insumo                           |

-----

## 📌 Observações

- Os arquivos Excel de origem devem estar disponíveis nos caminhos esperados por cada parser. Verifique os paths internos de cada módulo antes de executar.
- A inserção usa `if_exists="append"`, portanto executar o pipeline mais de uma vez duplicará os registros. Limpe as tabelas antes de uma reingestão completa.
- O arquivo `.env` nunca deve ser versionado — ele já está listado no `.gitignore`.