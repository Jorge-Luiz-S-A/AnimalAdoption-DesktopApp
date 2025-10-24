# models.py (com AuthUser)
"""
Modelos com usuários de sistema
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import bcrypt  # Para hash de senhas

Base = declarative_base()

class AuthUser(Base):
    """Usuários do sistema para login"""
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), default="usuario")  # admin, gestor, usuario
    
    def set_password(self, password):
        """Define senha com hash"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica senha"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_admin(self):
        """Verifica se é admin"""
        return self.nivel_acesso == "admin"

# ... outros modelos (Animal, User, Shelter, AdoptionProcess) permanecem iguais ...