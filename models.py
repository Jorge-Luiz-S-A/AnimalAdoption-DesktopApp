from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
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

    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(60))
    city = Column(String(120))
    adoption_preferences = Column(Text)
    approved = Column(Boolean, default=False)

    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")

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
