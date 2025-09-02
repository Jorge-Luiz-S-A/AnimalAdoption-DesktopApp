# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base

# Database setup
engine = create_engine("sqlite:///shelter.db", echo=False, future=True)

# Sessão com escopo
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
session = SessionLocal()

def init_db():
    """Cria tabelas e inicializa dados padrão."""
    Base.metadata.create_all(bind=engine)

    from models import Shelter, AuthUser

    if not session.query(Shelter).first():
        session.add(Shelter(name="Meu Abrigo"))

    if not session.query(AuthUser).filter_by(username="admin").first():
        admin = AuthUser(username="admin")
        admin.set_password("1234")  # senha inicial
        session.add(admin)

    try:
        session.commit()
    except:
        session.rollback()
        raise
