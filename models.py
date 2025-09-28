"""
Módulo de Modelos de Dados - SQLAlchemy ORM
-------------------------------------------
Este módulo define toda a estrutura de dados do sistema usando SQLAlchemy ORM.
Cada classe representa uma tabela no banco de dados com seus relacionamentos.

Entidades principais:
- Animal: Representa os animais disponíveis para adoção
- User: Representa os usuários/tutores do sistema
- Shelter: Representa os abrigos que acolhem os animais
- AdoptionProcess: Representa os processos de adoção em andamento
- AuthUser: Representa os usuários de sistema para autenticação

Características técnicas:
- Herdam de Base (declarative_base) para mapeamento ORM
- Relacionamentos bidirecionais com lazy loading
- Validações e métodos de negócio nas classes
- Hash seguro de senhas com bcrypt
- Constraints de integridade referencial

Padrões de design:
- Active Record: Modelos com métodos de negócio
- Separation of Concerns: Lógica separada por entidade
- Data Integrity: Constraints no banco e na aplicação
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
    sobre os animais disponíveis para adoção, incluindo características
    físicas, status de saúde e vinculação com abrigos.
    
    Atributos:
        id (int): Identificador único (chave primária)
        name (str): Nome do animal (obrigatório)
        species (str): Espécie (obrigatório)
        breed (str): Raça (opcional)
        age (int): Idade em anos (padrão 0)
        size (str): Porte (Pequeno, Médio, Grande)
        gender (str): Gênero (Macho, Fêmea)
        vaccinated (bool): Se foi vacinado
        neutered (bool): Se foi castrado
        temperament (str): Temperamento/comportamento
        health_history (str): Histórico de saúde
        status (str): Status de adoção
        location (str): Localização física
        shelter_id (int): ID do abrigo vinculado
        
    Relacionamentos:
        adoptions: Lista de processos de adoção
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
    Modelo que representa um usuário/tutor no sistema.
    
    Esta classe gerencia as informações dos tutores interessados em
    adotar animais, incluindo dados de contato e status de aprovação.
    
    Atributos:
        id (int): Identificador único
        name (str): Nome completo (obrigatório)
        email (str): Email único (obrigatório)
        phone (str): Telefone para contato
        city (str): Cidade de residência
        adoption_preferences (str): Observações/preferências
        approved (bool): Se está aprovado para adoção
        
    Relacionamentos:
        adoptions: Lista de processos de adoção do usuário
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
    
    Controla todo o fluxo de adoção desde o questionário inicial
    até a finalização, com registro de datas e status.
    
    Atributos:
        id (int): Identificador único
        animal_id (int): ID do animal (chave estrangeira)
        user_id (int): ID do usuário (chave estrangeira)
        status (str): Status atual do processo
        questionnaire_score (int): Pontuação do questionário
        virtual_visit_at (DateTime): Data da visita online
        in_person_visit_at (DateTime): Data da visita presencial
        docs_submitted (bool): Documentos entregues
        background_check_ok (bool): Verificação de antecedentes
        notes (str): Observações do processo
        
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
    virtual_visit_at = Column(DateTime)
    in_person_visit_at = Column(DateTime)
    docs_submitted = Column(Boolean, default=False)
    background_check_ok = Column(Boolean)
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
            elif self.status in ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado"]:
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
