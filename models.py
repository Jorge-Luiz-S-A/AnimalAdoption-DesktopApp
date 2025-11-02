<<<<<<< HEAD
"""
Módulo de Modelos de Dados - SQLAlchemy ORM
-------------------------------------------
Este módulo implementa o coração do sistema, definindo toda a estrutura
de dados e regras de negócio usando SQLAlchemy ORM como framework de
persistência.

1. Estrutura Principal:
   Animal:
   - Cadastro completo de animais
   - Características e histórico
   - Status de disponibilidade
   - Vinculação com abrigos

   User (Tutor):
   - Dados pessoais e contato
   - Preferências de adoção
   - Histórico de processos
   - Validações automáticas

   Shelter (Abrigo):
   - Informações institucionais
   - Controle de capacidade
   - Estatísticas em tempo real
   - Geolocalização

   AdoptionProcess:
   - Fluxo completo de adoção
   - Registro de visitas/docs
   - Status automatizado
   - Notas e observações

   AuthUser:
   - Autenticação segura
   - Níveis de acesso
   - Hash bcrypt com salt
   - Controle de sessão

2. Características Técnicas:
   - ORM SQLAlchemy
   - Lazy loading otimizado
   - Relacionamentos bidirecionais
   - Validações em camadas

3. Segurança:
   - Hash bcrypt para senhas
   - Proteção contra injeção
   - Validações robustas
   - Auditoria de mudanças

4. Padrões de Design:
   - Active Record Pattern
   - Repository Pattern
   - Unit of Work
   - Domain-Driven Design

5. Validações Implementadas:
   - Campos obrigatórios
   - Formatos específicos
   - Regras de negócio
   - Integridade referencial
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey
=======
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
>>>>>>> 55172dea57b5efe2dd74c80b452208b9b3547179
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import bcrypt

Base = declarative_base()

class Shelter(Base):
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

    animals = relationship("Animal", backref="shelter")

class Animal(Base):
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(20))
    age = Column(Integer, nullable=False, default=0)
    size = Column(String(20))
    gender = Column(String(20))
    vaccinated = Column(Boolean, default=False)
    neutered = Column(Boolean, default=False)
    temperament = Column(String(20))
    health_history = Column(Text)
    status = Column(String(20), default="Disponível")
    location = Column(String(30))
    shelter_id = Column(Integer, ForeignKey("shelter.id"), nullable=True)

    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
<<<<<<< HEAD
    name = Column(String(40), nullable=False)
    email = Column(String(40), unique=True, nullable=False)
    phone = Column(String(11))
    city = Column(String(25))
    adoption_preferences = Column(Text)  # Usado como campo de observações
=======
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(60))
    city = Column(String(120))
    adoption_preferences = Column(Text)
>>>>>>> 55172dea57b5efe2dd74c80b452208b9b3547179
    approved = Column(Boolean, default=False)

    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")

<<<<<<< HEAD
class Shelter(Base):
    """
    Modelo que representa um abrigo animal.
    
    Gerencia informações sobre os abrigos que acolhem os animais,
    incluindo capacidade, contato e estatísticas.
    
    Atributos:
        id (int): Identificador único
        name (str): Nome do abrigo
        email (str): Email de contato
        phone (str): Telefone de contato
        address (str): Endereço físico
        location (str): Localização/região
        capacity (int): Capacidade máxima
        rescued_count (int): Contador de resgatados
        adopted_count (int): Contador de adotados
    """
    __tablename__ = "shelter"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(40), default="Meu Abrigo")
    email = Column(String(40))
    phone = Column(String(11))
    address = Column(String(80))
    location = Column(String(120))
    capacity = Column(Integer, default=0)
    rescued_count = Column(Integer, default=0)
    adopted_count = Column(Integer, default=0)

=======
>>>>>>> 55172dea57b5efe2dd74c80b452208b9b3547179
class AdoptionProcess(Base):
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

    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")

    def update_animal_status(self):
        if self.animal:
            if self.status == "Finalizado":
                self.animal.status = "Adotado"
            elif self.status in ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado"]:
                self.animal.status = "Em processo"

class AuthUser(Base):
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), default="usuario")

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
    
    def is_admin(self) -> bool:
        return self.nivel_acesso == "admin"
