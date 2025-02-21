from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, JSON, DateTime, func, MetaData, create_engine, inspect
from databases import Database

# Configuração do Banco de Dados
DATABASE_URL: str = "sqlite:///./database.db"
database: Database = Database(DATABASE_URL)
metadata: MetaData = MetaData()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criação/Carregamento da Tabela "historias"
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

# Modelo Pydantic para representar uma História (opcional)
class Story(BaseModel):
    prompt: str
    groq: dict
    openai: dict
