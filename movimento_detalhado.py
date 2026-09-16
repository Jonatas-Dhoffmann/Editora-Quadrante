from ftplib import FTP
from dotenv import load_dotenv
from io import BytesIO
from sqlalchemy import create_engine, text

import pandas as pd
import os

# ==========================
# CONFIGURAÇÕES
# ==========================

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_FILE = os.getenv("FTP_FILE")

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# ==========================
# DOWNLOAD FTP PARA MEMÓRIA
# ==========================

ftp = FTP()
ftp.connect(FTP_HOST, FTP_PORT)
ftp.login(FTP_USER, FTP_PASSWORD)

print("Conectado ao FTP")

arquivo_memoria = BytesIO()

ftp.retrbinary(
    f"RETR {FTP_FILE}",
    arquivo_memoria.write
)

ftp.quit()

print("Arquivo carregado em memória")

arquivo_memoria.seek(0)

# ==========================
# LEITURA EXCEL
# ==========================

df = pd.read_excel(arquivo_memoria)

print(f"Linhas encontradas: {len(df)}")

# ==========================
# RENOMEIA COLUNAS
# ==========================

df = df.rename(columns={
    "EMPRESA": "empresa",
    "CNPJ": "cnpj",
    "EMISSAO": "emissao",
    "NOTAFISCAL": "nota_fiscal",
    "CFOP": "cfop",
    "CLIENTE": "cliente",
    "UF": "uf",
    "CODBARRAS": "isbn",
    "PRODUTO": "produto",
    "VLUNITARIO": "valor_unitario",
    "QUANTIDADE": "quantidade",
    "DESCONTO": "desconto",
    "VLTOTAL": "valor_total",
    "CATEGORIA": "categoria",
    "OPERACAO": "natureza_operacao",
    "TITULO_RESUMIDO": "titulo_resumido",
    "CLAS_CLIENTE": "classificacao_cliente",
    "CNPJ_CPF": "cpf_cnpj",
    "CIDADE": "cidade",
    "CAPA": "valor_capa",
    "CUSTO": "valor_custo",
    "CLAS_PRODUTO": "classificacao_produto",
    "CAT_PRODUTO": "categoria_produto",
    "AUTOR": "autor",
    "EDITORA": "editora",
    "COMPETENCIA": "competencia",
    "PEDIDO": "pedido",
    "PAIS": "pais",
    "FRETE": "frete",
    "ASSUNTO": "assunto",
    "PED_CLIENTE": "pedido_cliente",
    "CAT_VENDA": "categoria_venda",
    "TIPO": "tipo",
    "TRANSPORTADORA": "transportadora",
    "TIPOFRETE": "tipo_frete",
    "EVE_DESCRI": "descricao_evento",
    "ID_CLIENTE": "id_cliente",
    "AB_PEDIDO": "data_abertura_pedido",
    "EMAIL": "email",
    "TELEFONE": "telefone",
    "EXPEDICAO": "data_expedicao",
    "PESO_LIQ": "peso_liquido",
    "PESO_BRUTO": "peso_bruto",
    "VOLUME": "volume",
    "QUEM_ABRIU": "quem_abriu",
    "QUEM_FINALIZOU": "quem_finalizou",
    "LANCAMENTO": "lancamento",
    "FORMA_PAGTO": "forma_de_pagamento",
    "DAT_LIB": "data_liberacao",
    "LIB_MAC": "data_separacao_manuseio",
    "STATUS_PROD": "status_produto",
    "INDICADO": "indicado",
    "TIPO_PROJ": "tipo_projeto"
})

# ==========================
# MANTÉM SOMENTE COLUNAS EXISTENTES NO POSTGRES
# ==========================

colunas_destino = [
    "empresa",
    "cnpj",
    "emissao",
    "nota_fiscal",
    "cfop",
    "cliente",
    "uf",
    "isbn",
    "produto",
    "valor_unitario",
    "quantidade",
    "desconto",
    "valor_total",
    "categoria",
    "natureza_operacao",
    "titulo_resumido",
    "classificacao_cliente",
    "cpf_cnpj",
    "cidade",
    "valor_capa",
    "valor_custo",
    "classificacao_produto",
    "categoria_produto",
    "autor",
    "editora",
    "competencia",
    "pedido",
    "pais",
    "frete",
    "assunto",
    "pedido_cliente",
    "categoria_venda",
    "tipo",
    "transportadora",
    "tipo_frete",
    "descricao_evento",
    "id_cliente",
    "data_abertura_pedido",
    "email",
    "telefone",
    "data_expedicao",
    "peso_liquido",
    "peso_bruto",
    "volume",
    "quem_abriu",
    "quem_finalizou",
    "lancamento",
    "forma_de_pagamento",
    "data_liberacao",
    "data_separacao_manuseio",
    "status_produto",
    "indicado",
    "tipo_projeto"
]

df = df[colunas_destino]

# ==========================
# CONEXÃO POSTGRES
# ==========================

engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

# ==========================
# LIMPA TABELA
# ==========================

with engine.begin() as conn:
    conn.execute(
        text("TRUNCATE TABLE raw_movimento_detalhado")
    )

print("Tabela limpa")

# ==========================
# CARGA
# ==========================

df.to_sql(
    name="raw_movimento_detalhado",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print(f"Carga concluída: {len(df)} registros inseridos")