# Configuração básica do banco de dados SQLite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///shelter.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def init_db():
    # Cria tabelas básicas
    from models import Base
    Base.metadata.create_all(engine)