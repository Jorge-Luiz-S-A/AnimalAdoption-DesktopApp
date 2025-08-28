# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Shelter

# Database setup
engine = create_engine("sqlite:///shelter.db", echo=False, future=True)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

# Create tables
Base.metadata.create_all(engine)

# Bootstrap único Shelter
if not session.query(Shelter).first():
    session.add(Shelter(name="Meu Abrigo"))
    session.commit()
