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
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import bcrypt

# Base para todos os modelos - padrão SQLAlchemy
Base = declarative_base()

class Animal(Base):
    """
    Modelo que representa um animal no sistema do abrigo.
    
    Esta classe mapeia a tabela 'animals' e contém todas as informações
    sobre os animais disponíveis para adoção.
    
    Atributos:
        id (int): Identificador único (chave primária)
        name (str): Nome do animal (obrigatório)
        species (str): Espécie (obrigatório)
        breed (str): Raça (opcional)
        age (int): Idade em anos (padrão 0)
        size (str): Porte (Pequeno, Médio, Grande)
        gender (str): Gênero (Macho, Fêmea)
        temperament (str): Temperamento/comportamento
        status (str): Status de adoção
        location (str): Localização física (Abrigo)
        shelter_id (int): ID do abrigo vinculado
        
    Relacionamentos:
        adoptions: Lista de processos de adoção
        shelter: Abrigo onde o animal está alocado
    """
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(20))
    age = Column(Integer, nullable=False, default=0)
    size = Column(String(20))
    gender = Column(String(20))
    temperament = Column(String(20))
    status = Column(String(20), default="Disponível")
    location = Column(String(30))
    shelter_id = Column(Integer, ForeignKey("shelter.id"), nullable=True)

    # Relacionamentos
    adoptions = relationship("AdoptionProcess", back_populates="animal", lazy="selectin")
    shelter = relationship("Shelter", backref="animals")

class User(Base):
    """
    Modelo que representa um usuário/tutor no sistema.
    
    Esta classe gerencia as informações dos tutores interessados em
    adotar animais.
    
    Atributos:
        id (int): Identificador único
        name (str): Nome completo (obrigatório)
        email (str): Email único (obrigatório)
        phone (str): Telefone para contato
        city (str): Cidade de residência
        adoption_preferences (str): Observações
        
    Relacionamentos:
        adoptions: Lista de processos de adoção do usuário
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    email = Column(String(40), unique=True, nullable=False)
    phone = Column(String(11))
    city = Column(String(25))
    adoption_preferences = Column(Text)  # Usado como campo de observações
    approved = Column(Boolean, default=False)

    # Relacionamentos
    adoptions = relationship("AdoptionProcess", back_populates="user", lazy="selectin")

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
    capacity = Column(Integer, default=0)
    rescued_count = Column(Integer, default=0)
    adopted_count = Column(Integer, default=0)

class AdoptionProcess(Base):
    """
    Modelo que representa um processo de adoção.
    
    Controla todo o fluxo de adoção.
    
    Atributos:
        id (int): Identificador único
        animal_id (int): ID do animal (chave estrangeira)
        user_id (int): ID do usuário (chave estrangeira)
        status (str): Status atual do processo
        virtual_visit_at (DateTime): Data da visita online
        in_person_visit_at (DateTime): Data da visita presencial
        background_check_ok (bool): Verificação de antecedentes
        notes (str): Observações do processo
        
    Relacionamentos:
        animal: Animal sendo adotado
        user: Tutor adotante
    """
    __tablename__ = "adoptions"
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="questionnaire")
    virtual_visit_at = Column(DateTime)
    in_person_visit_at = Column(DateTime)
    notes = Column(Text)

    # Relacionamentos
    animal = relationship("Animal", back_populates="adoptions")
    user = relationship("User", back_populates="adoptions")

    def update_animal_status(self):
        """
        Atualiza automaticamente o status do animal baseado no processo.
        
        Esta função garante que o status do animal seja sempre consistente
        com o andamento do processo de adoção.
        
        Fluxo:
        - Processo finalizado → Animal marcado como "Adotado"
        - Processo em andamento → Animal marcado como "Em processo"
        """
        if self.animal:
            if self.status == "Finalizado":
                self.animal.status = "Adotado"
            elif self.status in ["Questionário", "Visita", "Documentos", "Aprovado"]:
                self.animal.status = "Em processo"

class AuthUser(Base):
    """
    Modelo para usuários de autenticação do sistema.
    
    Gerencia os usuários que podem acessar o sistema, com controle
    de níveis de acesso e autenticação segura com hash bcrypt.
    
    Atributos:
        id (int): Identificador único
        username (str): Nome de usuário único
        password_hash (str): Hash da senha
        nivel_acesso (str): Nível de acesso (admin, gestor, usuario)
    """
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), default="usuario")

    def set_password(self, password: str):
        """
        Define a senha do usuário com hash bcrypt.
        
        Args:
            password (str): Senha em texto claro
            
        Security:
            - Usa bcrypt para hash seguro
            - Gera salt automático
            - Protege contra rainbow tables
        """
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        
        Args:
            password (str): Senha em texto claro para verificar
            
        Returns:
            bool: True se a senha está correta, False caso contrário
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
    
    def is_admin(self) -> bool:
        """
        Verifica se o usuário tem permissão de administrador.
        
        Returns:
            bool: True se o usuário é admin, False caso contrário
        """
        return self.nivel_acesso == "admin"
