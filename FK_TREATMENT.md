# 🔐 Tratativa de Foreign Keys - Guia de Uso

## O que foi implementado?

Uma solução robusta para lidar com **Foreign Key Constraints** durante a inserção de dados. Agora o sistema:

### ✅ Valida automaticamente todas as Foreign Keys
- Remove registros com referências inválidas **antes de inserir**
- Evita erros de FK constraint violation
- Registra quantos registros foram removidos

### 📊 Mantém dados consistentes
- Filtra dados inválidos automaticamente
- Permite inserir dados sem erro
- Mostra relatório de dados removidos

## Arquivos modificados

### 1. **constraint_handler.py** (NOVO)
Módulo centralizado para gerenciar Foreign Keys:

```python
from constraint_handler import validate_all_foreign_keys, disable_foreign_keys, enable_foreign_keys
```

**Funções principais:**
- `validate_all_foreign_keys(df, table_name)` - Valida e filtra dados inválidos
- `disable_foreign_keys()` - Desabilita constraints (opcional)
- `enable_foreign_keys()` - Reabilita constraints (opcional)
- `validate_foreign_key()` - Valida uma FK específica

### 2. **insert_dataframes.py** (MODIFICADO)
Integração automática da validação:

```python
# Agora executa validação antes de inserir
df_new = validate_all_foreign_keys(df_new, table_name)
```

## Mapeamento de Foreign Keys

O sistema valida automaticamente estas FKs:

```
nf_movimentos:
  - codigo_fornecedor → fornecedores.codigo_fornecedor

nfse_medicoes:
  - codigo_fornecedor → fornecedores.codigo_fornecedor

solicitacoes:
  - codigo_fornecedor → fornecedores.codigo_fornecedor

base_cesta_apropriacoes:
  - (sem validação de FK)
```

## Exemplo de output

```
📥 Processando tabela: nf_movimentos
⚠️ 145 registros removidos por FK inválida em 'codigo_fornecedor'
📊 Total: 145 registros removidos em 'nf_movimentos'
✔ nf_movimentos: inseridas=2711 | descartadas=0
```

## Como adicionar nova validação de FK

Para adicionar validação de uma nova FK, edite `constraint_handler.py`:

```python
fk_mappings = {
    "nova_tabela": [
        ("coluna_fk", "tabela_referenciada", "coluna_referenciada"),
    ],
}
```

## Opções avançadas

### Desabilitar/Reabilitar constraints manualmente

```python
from constraint_handler import disable_foreign_keys, enable_foreign_keys

# Desabilitar
disable_foreign_keys()

# ... inserir dados ...

# Reabilitar
enable_foreign_keys()
```

### Validar FK específica

```python
from constraint_handler import validate_foreign_key

df_valido, removidos = validate_foreign_key(
    df,
    column_name="codigo_fornecedor",
    ref_table="fornecedores",
    ref_column="codigo_fornecedor"
)
```

## Benefícios

✅ **Automático** - Valida sem intervenção manual
✅ **Seguro** - Evita erros de integridade
✅ **Rastreável** - Mostra quantos registros foram removidos
✅ **Flexível** - Fácil adicionar novas validações
✅ **Não invasivo** - Não modifica o esquema do banco

## Próximos passos

Se precisar:
1. Restaurar Foreign Keys no schema - use o `models.py`
2. Adicionar mais validações - edite `constraint_handler.py`
3. Customizar comportamento - veja as opções em `constraint_handler.py`
