"""
Modelos de Dados do Sistema de Gerenciamento de Abrigo Animal
------------------------------------------------------------
Define todas as tabelas do banco de dados e seus relacionamentos usando SQLAlchemy ORM.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
import json
import bcrypt

# Base para todos os modelos
Base = declarative_base()

# Tabela de associação para favoritos (relação muitos-para-muitos)
user_favorites = Table(
    "user_favorites", 
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("animal_id", Integer, ForeignKey("animals.id"), primary_key=True),
)

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
        photo_urls_json (str): URLs das fotos em formato JSON
        shelter_id (int): ID do abrigo onde o animal está alocado (NOVO CAMPO)
        
    Relacionamentos:
        adoptions: Processos de adoção vinculados a este animal
        fosters: Lar temporário vinculado a este animal
        liked_by: Usuários que favoritaram este animal
        shelter: Abrigo onde o animal está alocado (NOVO RELACIONAMENTO)
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
    photo_urls_json = Column(Text, default="[]")
    shelter_id = Column(Integer, ForeignKey("shelter.id"), nullable=True)  # NOVO CAMPO

    # Relacionamentos
    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")
    fosters = relationship("Foster", back_populates="animal", lazy="selectin")
    liked_by = relationship("User", secondary=user_favorites, back_populates="favorites", lazy="selectin")
    shelter = relationship("Shelter", backref="animals")  # NOVO RELACIONAMENTO

    def photos(self):
        """Retorna a lista de URLs de fotos do animal."""
        try:
            return json.loads(self.photo_urls_json or "[]")
        except Exception:
            return []

class User(Base):
    """
    Modelo que representa um usuário do sistema.
    
    Atributos:
        id (int): Identificador único do usuário
        name (str): Nome do usuário (obrigatório)
        email (str): Email do usuário (obrigatório e único)
        phone (str): Telefone do usuário
        city (str): Cidade do usuário
        adoption_preferences (str): Preferências de adoção do usuário
        approved (bool): Se o usuário está aprovado para adoção
        
    Relacionamentos:
        favorites: Animais favoritados pelo usuário
        adoptions: Processos de adoção do usuário
        fosters: Lar temporário do usuário
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(60))
    city = Column(String(120))
    adoption_preferences = Column(Text)
    approved = Column(Boolean, default=False)

    # Relacionamentos
    favorites = relationship("Animal", secondary=user_favorites, back_populates="liked_by", lazy="selectin")
    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")
    fosters = relationship("Foster", back_populates="user", lazy="selectin")

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
        capacity (int): Capacidade máxima de animais do abrigo (NOVO CAMPO)
        rescued_count (int): Contador de animais resgatados
        adopted_count (int): Contador de animais adotados
        
    REMOVIDO: authenticity_verified (bool) - Campo removido conforme solicitação
    """
    __tablename__ = "shelter"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), default="Meu Abrigo")
    email = Column(String(120))
    phone = Column(String(60))
    address = Column(String(200))
    capacity = Column(Integer, default=0)  # NOVO CAMPO (substitui authenticity_verified)
    rescued_count = Column(Integer, default=0)
    adopted_count = Column(Integer, default=0)

class AdoptionProcess(Base):
    """
    Modelo que representa um processo de adoção.
    
    Atributos:
        id (int): Identificador único do processo
        animal_id (int): ID do animal sendo adotado (chave estrangeira)
        user_id (int): ID do usuário adotante (chave estrangeira)
        status (str): Status do processo (Questionário, Triagem, Visita, Documentos, Aprovado, Finalizado, Recusado)
        questionnaire_score (int): Pontuação do questionário de adoção
        virtual_visit_at (DateTime): Data e hora da visita virtual (NOVO CAMPO)
        in_person_visit_at (DateTime): Data e hora da visita presencial (NOVO CAMPO)
        docs_submitted (bool): Se os documentos foram submetidos
        background_check_ok (bool): Se a verificação de antecedentes está OK
        notes (str): Observações sobre o processo
        
    Relacionamentos:
        animal: Animal sendo adotado
        user: Usuário adotante
    """
    __tablename__ = "adoptions"
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="questionnaire")
    questionnaire_score = Column(Integer)
    virtual_visit_at = Column(DateTime)  # NOVO CAMPO
    in_person_visit_at = Column(DateTime)  # NOVO CAMPO
    docs_submitted = Column(Boolean, default=False)
    background_check_ok = Column(Boolean)
    notes = Column(Text)

    # Relacionamentos
    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")

class Foster(Base):
    """
    Modelo que representa um lar temporário (foster).
    
    Atributos:
        id (int): Identificador único do foster
        animal_id (int): ID do animal em lar temporário (chave estrangeira)
        user_id (int): ID do usuário que fornece o lar temporário (chave estrangeira)
        start_date (Date): Data de início do lar temporário
        end_date (Date): Data de término do lar temporário
        active (bool): Se o lar temporário está ativo
        notes (str): Observações sobre o lar temporário
        
    Relacionamentos:
        animal: Animal em lar temporário
        user: Usuário que fornece o lar temporário
    """
    __tablename__ = "fosters"
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    notes = Column(Text)

    # Relacionamentos
    animal = relationship("Animal", back_populates="fosters")
    user = relationship("User", back_populates="fosters")

class AuthUser(Base):
    """
    Modelo que representa um usuário de autenticação do sistema.
    
    Atributos:
        id (int): Identificador único do usuário
        username (str): Nome de usuário (obrigatório e único)
        password_hash (str): Hash da senha do usuário (obrigatório)
    """
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def set_password(self, password: str):
        """Define a senha do usuário com hash bcrypt."""
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
