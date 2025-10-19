<<<<<<< HEAD
# models.py (atualizado com Shelter)
"""
Modelos completos com abrigos
=======
# models.py (com adoções)
"""
Modelos completos do sistema
>>>>>>> fb9618de721d2e3061f964d07373ccd9f57eab4f
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Shelter(Base):
    """Modelo de abrigo"""
    __tablename__ = "shelter"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), default="Meu Abrigo")
    email = Column(String(120))
    phone = Column(String(60))
    address = Column(String(200))
    capacity = Column(Integer, default=0)
    
    # Relacionamento com animais
    animals = relationship("Animal", backref="shelter")

class Animal(Base):
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    species = Column(String(50))
    breed = Column(String(120))
    age = Column(Integer, default=0)
    size = Column(String(20))
    gender = Column(String(20))
    status = Column(String(20), default="Disponível")
    health_history = Column(Text)
<<<<<<< HEAD
    shelter_id = Column(Integer, ForeignKey("shelter.id"))  # Vinculação com abrigo
    
=======
    
    # Relacionamento com adoções
>>>>>>> fb9618de721d2e3061f964d07373ccd9f57eab4f
    adoptions = relationship("AdoptionProcess", back_populates="animal")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120))
    phone = Column(String(60))
    city = Column(String(120))
    approved = Column(Boolean, default=False)
<<<<<<< HEAD
    adoption_preferences = Column(Text)
    
    adoptions = relationship("AdoptionProcess", back_populates="user")

class AdoptionProcess(Base):
=======
    
    # Relacionamento com adoções
    adoptions = relationship("AdoptionProcess", back_populates="user")

class AdoptionProcess(Base):
    """Processo de adoção"""
>>>>>>> fb9618de721d2e3061f964d07373ccd9f57eab4f
    __tablename__ = "adoptions"
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
<<<<<<< HEAD
    status = Column(String(30), default="questionnaire")
    created_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    
    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")
=======
    status = Column(String(30), default="questionnaire")  # Status do processo
    created_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)  # Observações
    
    # Relacionamentos
    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")
>>>>>>> fb9618de721d2e3061f964d07373ccd9f57eab4f
