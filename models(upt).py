# models.py (atualizado)
"""
Modelos com mais campos
"""
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Animal(Base):
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    species = Column(String(50))
    breed = Column(String(120))
    age = Column(Integer, default=0)
    size = Column(String(20))  # Porte (P, M, G)
    gender = Column(String(20))  # Gênero
    status = Column(String(20), default="Disponível")
    health_history = Column(Text)  # Histórico de saúde

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120))
    phone = Column(String(60))
    city = Column(String(120))
    approved = Column(Boolean, default=False)  # Aprovado para adoção
