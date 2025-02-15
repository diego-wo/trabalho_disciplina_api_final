from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, JSON, DateTime, func, MetaData
from sqlalchemy import create_engine, inspect
from databases import Database

DATABASE_URL = "sqlite:///./database.db"

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

if not inspect(engine).has_table("historias"):
    historias = Table(
        "historias",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("data_criacao", DateTime, server_default=func.now()),
        Column("prompt", String),
        Column("groq", JSON),
        Column("openai", JSON),
    )
    metadata.create_all(engine)
else:
    historias = Table("historias", metadata, autoload_with=engine)

class NomeGrupo(str, Enum):
    operacoes = "Operações matemáticas simples"
    teste = "Teste"

class TipoOperacao(str, Enum):
    soma = "soma"
    subtracao = "subtracao"
    multiplicacao = "multiplicacao"
    divisao = "divisao"

class Numero(BaseModel):
    numero1: int
    numero2: int

class Resultado(BaseModel):
    resultado: int
