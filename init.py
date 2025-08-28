# init.py
"""
Abrigo Animal - Sistema de Gerenciamento

Este pacote contém o sistema completo de gerenciamento de abrigo animal.
"""

# Importações principais para facilitar o acesso
from .models import Animal, User, Shelter, AdoptionProcess, Foster
from .database import session, engine
from .utils import (
    STATUSES, ADOPTION_STEPS, SIZES, GENDERS,
    parse_bool, parse_int, parse_date_str, parse_dt_str,
    yes_no, combobox_set
)
from .base_tab import BaseTab
from .animals_tab import AnimalsTab

# Versão do sistema
__version__ = "1.0.0"
__author__ = "Sistema de Gerenciamento de Abrigo Animal"
__description__ = "Sistema completo para gerenciamento de abrigo animal com CRUD de animais, usuários, processos de adoção e mais"

# Lista de exportações para importação com *
__all__ = [
    # Models
    'Animal', 'User', 'Shelter', 'AdoptionProcess', 'Foster',
    
    # Database
    'session', 'engine',
    
    # Utils
    'STATUSES', 'ADOPTION_STEPS', 'SIZES', 'GENDERS',
    'parse_bool', 'parse_int', 'parse_date_str', 'parse_dt_str',
    'yes_no', 'combobox_set',
    
    # GUI Components
    'BaseTab', 'AnimalsTab',
    
    # Metadata
    '__version__', '__author__', '__description__'
]

# Inicialização do sistema
def init_system():
    """Inicializa o sistema verificando o banco de dados"""
    from .database import Base
    # Cria todas as tabelas se não existirem
    Base.metadata.create_all(engine)
    
    # Verifica se existe um abrigo padrão
    from .models import Shelter
    if not session.query(Shelter).first():
        default_shelter = Shelter(name="Meu Abrigo")
        session.add(default_shelter)
        session.commit()
        print("Abrigo padrão criado com sucesso!")
    
    print(f"Sistema de Gerenciamento de Abrigo Animal v{__version__} inicializado!")

# Executa a inicialização quando o pacote é importado
init_system()
