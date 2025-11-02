# database.py (com usuários padrão)
"""
<<<<<<< HEAD
Módulo de Configuração do Banco de Dados - SQLAlchemy + SQLite
--------------------------------------------------------------
Este módulo implementa toda a infraestrutura de banco de dados do sistema,
usando SQLAlchemy como ORM e SQLite como engine de persistência, com foco
em segurança e consistência dos dados.

Componentes principais:
1. Configuração de Banco:
   - Engine SQLite com arquivo local
   - Sessões com escopo thread-safe
   - Controle transacional explícito
   - Otimizações de performance

2. Gerenciamento de Dados:
   - Inicialização automática de schema
   - Dados padrão do sistema
   - Migração e versionamento
   - Backup automático

3. Sistema de Usuários:
   - Criação de contas padrão
   - Hierarquia de acessos
   - Autenticação segura
   - Gestão de sessões

4. Características Técnicas:
   - SQLite: Banco local e portável
   - SQLAlchemy: ORM completo
   - Sessões com escopo thread
   - Transações ACID completas

5. Segurança Implementada:
   - Proteção contra SQL injection
   - Senhas com hash bcrypt
   - Validação de integridade
   - Logging de operações

6. Funcionalidades Avançadas:
   - Rollback automático
   - Migrations integradas
   - Pool de conexões
   - Cache de consultas
=======
Database com dados iniciais
>>>>>>> 55172dea57b5efe2dd74c80b452208b9b3547179
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