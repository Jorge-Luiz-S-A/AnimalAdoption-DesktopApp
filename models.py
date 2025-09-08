"""
Modelos de Dados do Sistema de Gerenciamento de Abrigo Animal
------------------------------------------------------------
Define todas as tabelas do banco de dados e seus relacionamentos usando SQLAlchemy ORM.
Versão simplificada sem Foster, Favoritos e Fotos.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import bcrypt

# Base para todos os modelos
Base = declarative_base()

class Animal(Base):
    """
    Modelo que representa um animal no sistema.
    
    Atributos:
        id (int): Identificador único do animal
        name (str): Nome do animal (obrigatório)
        species (str): Espécie do animal (obrigatório)
        breed (str): Raça do animal
        age (int): Idade do animal em anos
        size (str): Porte do animal (Pequeno, Médio, Grande)
        gender (str): Gênero do animal (Macho, Fêmea)
        vaccinated (bool): Se o animal foi vacinado
        neutered (bool): Se o animal foi castrado
        temperament (str): Temperamento do animal
        health_history (str): Histórico de saúde do animal
        status (str): Status de adoção (Disponível, Em processo, Adotado, Indisponível)
        location (str): Localização física do animal
        shelter_id (int): ID do abrigo onde o animal está alocado
        
    Relacionamentos:
        adoptions: Processos de adoção vinculados a este animal
        shelter: Abrigo onde o animal está alocado
    """
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(120))
    age = Column(Integer, nullable=False, default=0)
    size = Column(String(20))
    gender = Column(String(20))
    vaccinated = Column(Boolean, default=False)
    neutered = Column(Boolean, default=False)
    temperament = Column(String(250))
    health_history = Column(Text)
    status = Column(String(20), default="available")
    location = Column(String(120))
    shelter_id = Column(Integer, ForeignKey("shelter.id"), nullable=True)

    # Relacionamentos
    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")
    shelter = relationship("Shelter", backref="animals")

class User(Base):
    """
    Modelo que representa um usuário do sistema.
    
    Atributos:
        id (int): Identificador único do usuario
        name (str): Nome do usuario (obrigatório)
        email (str): Email do usuario (obrigatório e único)
        phone (str): Telefone do usuario
        city (str): Cidade do usuario
        adoption_preferences (str): Preferências de adoção do usuario (usado como observações)
        approved (bool): Se o usuario está aprovado para adoção
        
    Relacionamentos:
        adoptions: Processos de adoção do usuario
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(60))
    city = Column(String(120))
    adoption_preferences = Column(Text)  # Usado como campo de observações
    approved = Column(Boolean, default=False)

    # Relacionamentos
    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")

class Shelter(Base):
    """
    Modelo que representa um abrigo animal.
    
    Atributos:
        id (int): Identificador único do abrigo
        name (str): Nome do abrigo
        email (str): Email de contato do abrigo
        phone (str): Telefone de contato do abrigo
        address (str): Endereço físico do abrigo
        location (str): Localização/região do abrigo
        capacity (int): Capacidade máxima de animais do abrigo
        rescued_count (int): Contador de animais resgatados
        adopted_count (int): Contador de animais adotados
    """
    __tablename__ = "shelter"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), default="Meu Abrigo")
    email = Column(String(120))
    phone = Column(String(60))
    address = Column(String(200))
    location = Column(String(120))
    capacity = Column(Integer, default=0)
    rescued_count = Column(Integer, default=0)
    adopted_count = Column(Integer, default=0)

class AdoptionProcess(Base):
    """
    Modelo que representa um processo de adoção.
    
    Atributos:
        id (int): Identificador único do processo
        animal_id (int): ID do animal sendo adotado (chave estrangeira)
        user_id (int): ID do usuario adotante (chave estrangeira)
        status (str): Status do processo (Questionário, Triagem, Visita, Documentos, Aprovado, Finalizado, Recusado)
        questionnaire_score (int): Pontuação do questionário de adoção
        virtual_visit_at (DateTime): Data e hora da visita virtual
        in_person_visit_at (DateTime): Data e hora da visita presencial
        docs_submitted (bool): Se os documentos foram submetidos
        background_check_ok (bool): Se a verificação de antecedentes está OK
        notes (str): Observações sobre o processo
        
    Relacionamentos:
        animal: Animal sendo adotado
        user: Usuario adotante
    """
    __tablename__ = "adoptions"
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="questionnaire")
    questionnaire_score = Column(Integer)
    virtual_visit_at = Column(DateTime)
    in_person_visit_at = Column(DateTime)
    docs_submitted = Column(Boolean, default=False)
    background_check_ok = Column(Boolean)
    notes = Column(Text)

    # Relacionamentos
    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")

    def update_animal_status(self):
        """Atualiza o status do animal baseado no status da adoção"""
        if self.animal:
            if self.status == "Finalizado":
                self.animal.status = "Adotado"
            elif self.status in ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado"]:
                self.animal.status = "Em processo"

class AuthUser(Base):
    """
    Modelo que representa um usuario de autenticação do sistema.
    
    Atributos:
        id (int): Identificador único do usuario
        username (str): Nome de usuario (obrigatório e único)
        password_hash (str): Hash da senha do usuario (obrigatório)
        nivel_acesso (str): Nível de acesso do usuario (admin, gestor, usuario)
    """
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), default="usuario")

    def set_password(self, password: str):
        """Define a senha do usuario com hash bcrypt."""
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
    
    def is_admin(self) -> bool:
        """Verifica se o usuario tem permissão de administrador."""
        return self.nivel_acesso == "admin"
