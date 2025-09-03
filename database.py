"""
Configuração do Banco de Dados
-------------------------------
Configura a conexão com o banco de dados SQLite e inicializa a sessão do SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base

# Configuração da engine do banco de dados SQLite
engine = create_engine("sqlite:///shelter.db", echo=False, future=True)

# Configuração da sessão do SQLAlchemy
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
session = SessionLocal()

def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas e dados padrão.
    
    Cria:
    - Todas as tabelas definidas nos modelos
    - Um abrigo padrão se não existir
    - Um usuário admin padrão se não existir
    """
    Base.metadata.create_all(bind=engine)

    from models import Shelter, AuthUser

    # Cria abrigo padrão se não existir
    if not session.query(Shelter).first():
        session.add(Shelter(name="Meu Abrigo"))

    # Cria usuário admin padrão se não existir
    if not session.query(AuthUser).filter_by(username="admin").first():
        admin = AuthUser(username="admin")
        admin.set_password("1234")
        session.add(admin)

    try:
        session.commit()
    except:
        session.rollback()
        raise
