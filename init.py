"""
Pacote Principal - Sistema de Gerenciamento de Abrigo Animal
------------------------------------------------------------
Módulo principal que exporta todos os componentes do sistema.
Versão 1.1.0 simplificada sem Foster, Favoritos e Fotos.
"""

from .models import Animal, User, Shelter, AdoptionProcess
from .database import session, engine
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

__version__ = "1.1.0"
__author__ = "Sistema de Gerenciamento de Abrigo Animal"
__description__ = "Sistema completo para gerenciamento de abrigo animal com CRUD de animais, usuários, processos de adoção e mais"

__all__ = [
    'Animal', 'User', 'Shelter', 'AdoptionProcess',
    'session', 'engine',
    'STATUSES', 'ADOPTION_STEPS', 'SIZES', 'GENDERS',
    'parse_bool', 'parse_int', 'parse_date_str', 'parse_dt_str',
    'yes_no', 'combobox_set',
    'BaseTab', 'AnimalsTab', 'AdoptionsTab', 'UsersTab', 'ShelterTab', 'SearchTab',
    '__version__', '__author__', '__description__'
]

def init_system():
    """
    Inicializa o sistema criando tabelas e dados padrão.
    
    Cria:
    - Todas as tabelas do banco de dados
    - Abrigo padrão se não existir
    """
    from .database import Base
    Base.metadata.create_all(engine)

    from .models import Shelter
    if not session.query(Shelter).first():
        default_shelter = Shelter(name="Meu Abrigo", location="", capacity=50)
        session.add(default_shelter)
        session.commit()
        print("Abrigo padrão criado com sucesso!")

    print(f"Sistema de Gerenciamento de Abrigo Animal v{__version__} inicializado!")

# Inicializa o sistema automaticamente ao importar o pacote
init_system()
