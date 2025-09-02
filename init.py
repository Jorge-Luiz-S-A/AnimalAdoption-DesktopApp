# init.py
"""
Abrigo Animal - Sistema de Gerenciamento
"""

from .models import Animal, User, Shelter, AdoptionProcess, Foster
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

__version__ = "1.0.0"
__author__ = "Sistema de Gerenciamento de Abrigo Animal"
__description__ = "Sistema completo para gerenciamento de abrigo animal com CRUD de animais, usuários, processos de adoção e mais"

__all__ = [
    'Animal', 'User', 'Shelter', 'AdoptionProcess', 'Foster',
    'session', 'engine',
    'STATUSES', 'ADOPTION_STEPS', 'SIZES', 'GENDERS',
    'parse_bool', 'parse_int', 'parse_date_str', 'parse_dt_str',
    'yes_no', 'combobox_set',
    'BaseTab', 'AnimalsTab', 'AdoptionsTab', 'UsersTab', 'ShelterTab', 'SearchTab',
    '__version__', '__author__', '__description__'
]

def init_system():
    from .database import Base
    Base.metadata.create_all(engine)

    from .models import Shelter
    if not session.query(Shelter).first():
        default_shelter = Shelter(name="Meu Abrigo")
        session.add(default_shelter)
        session.commit()
        print("Abrigo padrão criado com sucesso!")

    print(f"Sistema de Gerenciamento de Abrigo Animal v{__version__} inicializado!")

init_system()
