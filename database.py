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

# LISTA DE USUÁRIOS PADRÃO DO SISTEMA
USUARIOS_PADRAO = [
    {"username": "admin", "password": "admin123", "nivel_acesso": "admin"},
    {"username": "gestor", "password": "gestor123", "nivel_acesso": "gestor"},
    {"username": "atendente", "password": "atendente123", "nivel_acesso": "usuario"},
]

def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas e dados padrão.
    
    Cria:
    - Todas as tabelas definidas nos modelos
    - Um abrigo padrão se não existir
    - Múltiplos usuários padrão com diferentes níveis de acesso
    """
    Base.metadata.create_all(bind=engine)

    from models import Shelter, AuthUser

    # Cria abrigo padrão se não existir
    if not session.query(Shelter).first():
        session.add(Shelter(name="Meu Abrigo", capacity=50))

    # Cria múltiplos usuários padrão
    for usuario_info in USUARIOS_PADRAO:
        if not session.query(AuthUser).filter_by(username=usuario_info["username"]).first():
            usuario = AuthUser(
                username=usuario_info["username"],
                nivel_acesso=usuario_info["nivel_acesso"]
            )
            usuario.set_password(usuario_info["password"])
            session.add(usuario)
            print(f"Usuário padrão criado: {usuario_info['username']}")

    try:
        session.commit()
        print("Banco de dados inicializado com sucesso!")
        print(f"Usuários disponíveis: {[u['username'] for u in USUARIOS_PADRAO]}")
    except Exception as e:
        session.rollback()
        print(f"Erro ao inicializar banco de dados: {e}")
        raise

def listar_usuarios():
    """
    Lista todos os usuários do sistema.
    
    Returns:
        list: Lista de usuários cadastrados
    """
    from models import AuthUser
    return session.query(AuthUser).all()

def criar_usuario(username, password, nivel_acesso="usuario"):
    """
    Cria um novo usuário no sistema.
    
    Args:
        username (str): Nome de usuário
        password (str): Senha do usuário
        nivel_acesso (str): Nível de acesso (opcional)
        
    Returns:
        bool: True se usuário foi criado, False se já existe
    """
    from models import AuthUser
    
    if session.query(AuthUser).filter_by(username=username).first():
        print(f"Usuário '{username}' já existe!")
        return False
    
    usuario = AuthUser(username=username, nivel_acesso=nivel_acesso)
    usuario.set_password(password)
    session.add(usuario)
    
    try:
        session.commit()
        print(f"Usuário '{username}' criado com sucesso!")
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao criar usuário: {e}")
        return False

def verificar_usuario(username, password):
    """
    Verifica se as credenciais de usuário são válidas.
    
    Args:
        username (str): Nome de usuário
        password (str): Senha
        
    Returns:
        bool: True se credenciais são válidas, False caso contrário
    """
    from models import AuthUser
    
    usuario = session.query(AuthUser).filter_by(username=username).first()
    if usuario and usuario.check_password(password):
        return True
    return False
