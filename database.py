"""
Módulo de Configuração do Banco de Dados - SQLAlchemy + SQLite
--------------------------------------------------------------
Este módulo configura toda a infraestrutura de persistência de dados
do sistema usando SQLAlchemy ORM com SQLite como banco de dados.

Funcionalidades principais:
- Configuração da engine de conexão com SQLite
- Gerenciamento de sessões do SQLAlchemy
- Inicialização automática do banco com dados padrão
- Criação de usuários padrão do sistema
- Funções utilitárias para autenticação

Características técnicas:
- SQLite: Banco embutido, não requer servidor externo
- SQLAlchemy ORM: Mapeamento objeto-relacional avançado
- Sessões com escopo: Gerencia automaticamente conexões
- Transações: Controle completo de commit/rollback

Estrutura de inicialização:
- Cria todas as tabelas definidas nos modelos
- Cria abrigo padrão se não existir
- Cria múltiplos usuários com diferentes níveis de acesso
- Garante integridade do schema
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base

# Configuração da engine do SQLite
# "sqlite:///shelter.db" - Cria arquivo shelter.db no diretório atual
# echo=False - Desativa log SQL (para produção)
# future=True - Habilita comportamentos da versão 2.0
engine = create_engine("sqlite:///shelter.db", echo=False, future=True)

# Configuração da sessão com escopo
# scoped_session: Fornece a mesma sessão para mesma thread
# autoflush=False: Controle manual de flush
# autocommit=False: Controle manual de transações
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
session = SessionLocal()

# LISTA DE USUÁRIOS PADRÃO DO SISTEMA
# Estes usuários são criados automaticamente na inicialização
USUARIOS_PADRAO = [
    {"username": "admin", "password": "admin123", "nivel_acesso": "admin"},
    {"username": "gestor", "password": "gestor123", "nivel_acesso": "gestor"},
    {"username": "atendente", "password": "atendente123", "nivel_acesso": "usuario"},
]

def init_db():
    """
    Inicializa o banco de dados criando tabelas e dados padrão.
    
    Esta função é executada automaticamente na inicialização do sistema
    e garante que o banco esteja pronto para uso com:
    - Todas as tabelas criadas
    - Dados iniciais necessários
    - Usuários padrão para acesso
    
    Fluxo de execução:
    1. Cria todas as tabelas baseadas nos modelos
    2. Cria abrigo padrão se não existir
    3. Cria usuários padrão com diferentes níveis de acesso
    4. Confirma todas as alterações
    
    Exceções são tratadas com rollback para manter consistência.
    """
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)

    from models import Shelter, AuthUser

    # Cria abrigo padrão se não existir nenhum
    if not session.query(Shelter).first():
        session.add(Shelter(name="Meu Abrigo", capacity=50))

    # Cria múltiplos usuários padrão
    for usuario_info in USUARIOS_PADRAO:
        # Verifica se o usuário já existe
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
        list: Lista de objetos AuthUser com todos os usuários cadastrados
    """
    from models import AuthUser
    return session.query(AuthUser).all()

def criar_usuario(username, password, nivel_acesso="usuario"):
    """
    Cria um novo usuário no sistema.
    
    Args:
        username (str): Nome de usuário único
        password (str): Senha em texto claro (será hasheada)
        nivel_acesso (str): Nível de acesso (admin, gestor, usuario)
        
    Returns:
        bool: True se usuário foi criado, False se já existe
        
    Exemplo de uso:
        criar_usuario("novo_user", "senha123", "usuario")
    """
    from models import AuthUser
    
    # Verifica se usuário já existe
    if session.query(AuthUser).filter_by(username=username).first():
        print(f"Usuário '{username}' já existe!")
        return False
    
    # Cria novo usuário
    usuario = AuthUser(username=username, nivel_acesso=nivel_acesso)
    usuario.set_password(password)  # Gera hash da senha
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
        password (str): Senha em texto claro
        
    Returns:
        bool: True se credenciais são válidas, False caso contrário
        
    Exemplo de uso:
        if verificar_usuario("admin", "admin123"):
            print("Login válido")
    """
    from models import AuthUser
    
    # Busca usuário pelo username
    usuario = session.query(AuthUser).filter_by(username=username).first()
    
    # Verifica se usuário existe e senha está correta
    if usuario and usuario.check_password(password):
        return True
    return False
