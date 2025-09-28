"""
Pacote Principal - Sistema de Gerenciamento de Abrigo Animal
------------------------------------------------------------
Este é o pacote principal que exporta todos os componentes do sistema
para facilitar imports organizados e controle de versão.

Funcionalidades do pacote:
- Exportação organizada de todos os módulos
- Controle de versão centralizado
- Inicialização automática do sistema
- Interface de import limpa

Estrutura de exports:
- Models: Classes de entidade do banco
- Database: Configuração e sessão do banco
- Utils: Funções auxiliares e constantes
- Tabs: Todas as abas da interface
- Metadados: Versão, autor, descrição

Versão 1.1.0 - Características:
- Sistema completo de gerenciamento de abrigo
- Interface desktop com tkinter
- Banco SQLite com SQLAlchemy ORM
- Autenticação segura com níveis de acesso
- CRUD completo para todas as entidades
"""

from .models import Animal, User, Shelter, AdoptionProcess, AuthUser
from .database import session, engine, init_db
from .utils import (
    STATUSES, ADOPTION_STEPS, SIZES, GENDERS,
    parse_bool, parse_int, parse_date_str, parse_dt_str,
    yes_no, combobox_set
)
from .base_tab import BaseTab
from .animals_tab import AnimalsTab
from .adoptions_tab import AdoptionsTab
from .users_tab import UsersTab
from .shelter_tab import ShelterTab
from .search_tab import SearchTab
from .adm_tab import AdmTab
from .login import login_screen

# ========== METADADOS DO PACOTE ==========
__version__ = "1.1.0"
__author__ = "Sistema de Gerenciamento de Abrigo Animal"
__description__ = "Sistema completo para gerenciamento de abrigo animal com CRUD de animais, usuários, processos de adoção e mais"

# ========== INTERFACE PÚBLICA DO PACOTE ==========
__all__ = [
    # Models
    'Animal', 'User', 'Shelter', 'AdoptionProcess', 'AuthUser',
    
    # Database
    'session', 'engine', 'init_db',
    
    # Utils
    'STATUSES', 'ADOPTION_STEPS', 'SIZES', 'GENDERS',
    'parse_bool', 'parse_int', 'parse_date_str', 'parse_dt_str',
    'yes_no', 'combobox_set',
    
    # Tabs
    'BaseTab', 'AnimalsTab', 'AdoptionsTab', 'UsersTab', 
    'ShelterTab', 'SearchTab', 'AdmTab',
    
    # Login
    'login_screen',
    
    # Metadata
    '__version__', '__author__', '__description__'
]

def init_system():
    """
    Inicializa o sistema criando tabelas e dados padrão.
    
    Esta função é chamada automaticamente ao importar o pacote
    e garante que o sistema esteja pronto para uso.
    
    Cria:
    - Todas as tabelas do banco de dados
    - Abrigo padrão se não existir
    - Usuários padrão para acesso
    
    Exemplo de uso:
        from shelter_system import init_system
        init_system()
    """
    from .database import Base
    
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(engine)

    from .models import Shelter
    
    # Cria abrigo padrão se não existir nenhum
    if not session.query(Shelter).first():
        default_shelter = Shelter(name="Abrigo Central", location="São Paulo", capacity=50)
        session.add(default_shelter)
        session.commit()
        print("Abrigo padrão criado com sucesso!")

    print(f"Sistema de Gerenciamento de Abrigo Animal v{__version__} inicializado!")

# Inicializa o sistema automaticamente ao importar o pacote
init_system()
