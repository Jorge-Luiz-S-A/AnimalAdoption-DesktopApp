# database.py
"""
Configuração básica do banco SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Conecta com o banco SQLite
engine = create_engine("sqlite:///shelter.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def init_db():
    """Cria todas as tabelas no banco"""
    from models import Base
    Base.metadata.create_all(engine)
    print("Banco inicializado!")
