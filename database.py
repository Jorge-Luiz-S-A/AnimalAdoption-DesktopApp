# database.py (com usuários padrão)
"""
Database com dados iniciais
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, AuthUser, Shelter

engine = create_engine("sqlite:///shelter.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Usuários padrão do sistema
USUARIOS_PADRAO = [
    {"username": "admin", "password": "admin123", "nivel_acesso": "admin"},
    {"username": "gestor", "password": "gestor123", "nivel_acesso": "gestor"},
    {"username": "atendente", "password": "atendente123", "nivel_acesso": "usuario"},
]

def init_db():
    """Inicializa banco com dados padrão"""
    Base.metadata.create_all(bind=engine)
    
    # Cria abrigo padrão
    if not session.query(Shelter).first():
        session.add(Shelter(name="Abrigo Central", capacity=50))
    
    # Cria usuários padrão
    for user_info in USUARIOS_PADRAO:
        if not session.query(AuthUser).filter_by(username=user_info["username"]).first():
            usuario = AuthUser(
                username=user_info["username"],
                nivel_acesso=user_info["nivel_acesso"]
            )
            usuario.set_password(user_info["password"])
            session.add(usuario)
            print(f"Usuário criado: {user_info['username']}")
    
    try:
        session.commit()
        print("Banco inicializado com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")