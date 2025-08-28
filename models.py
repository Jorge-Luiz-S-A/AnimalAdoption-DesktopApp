# models.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
import json

Base = declarative_base()

# Association table - Favorites
user_favorites = Table(
    "user_favorites", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("animal_id", Integer, ForeignKey("animals.id"), primary_key=True),
)

class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(120))
    age = Column(Integer, nullable=False, default=0)  # anos
    size = Column(String(20))  # pequeno, médio, grande
    gender = Column(String(20))  # macho, fêmea
    vaccinated = Column(Boolean, default=False)
    neutered = Column(Boolean, default=False)
    temperament = Column(String(250))
    health_history = Column(Text)
    status = Column(String(20), default="available")  # available, in_process, adopted
    location = Column(String(120))
    photo_urls_json = Column(Text, default="[]")

    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")
    fosters = relationship("Foster", back_populates="animal", lazy="selectin")
    liked_by = relationship("User", secondary=user_favorites, back_populates="favorites", lazy="selectin")

    def photos(self):
        try:
            return json.loads(self.photo_urls_json or "[]")
        except Exception:
            return []

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(60))
    city = Column(String(120))
    adoption_preferences = Column(Text)  # JSON
    approved = Column(Boolean, default=False)

    favorites = relationship("Animal", secondary=user_favorites, back_populates="liked_by", lazy="selectin")
    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")
    fosters = relationship("Foster", back_populates="user", lazy="selectin")

class Shelter(Base):
    __tablename__ = "shelter"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), default="Meu Abrigo")
    email = Column(String(120))
    phone = Column(String(60))
    address = Column(String(200))
    authenticity_verified = Column(Boolean, default=False)
    rescued_count = Column(Integer, default=0)
    adopted_count = Column(Integer, default=0)

class AdoptionProcess(Base):
    __tablename__ = "adoptions"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="questionnaire")  # questionnaire, screening, visit, docs, approved, finalized, declined
    questionnaire_score = Column(Integer)
    virtual_visit_at = Column(DateTime)
    in_person_visit_at = Column(DateTime)
    docs_submitted = Column(Boolean, default=False)
    background_check_ok = Column(Boolean)  # None/True/False
    notes = Column(Text)

    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")

class Foster(Base):
    __tablename__ = "fosters"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    notes = Column(Text)

    animal = relationship("Animal", back_populates="fosters")
    user = relationship("User", back_populates="fosters")
