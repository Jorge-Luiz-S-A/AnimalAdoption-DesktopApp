"""
Módulo Principal - Aplicação Desktop do Sistema de Abrigo Animal
----------------------------------------------------------------
Este é o ponto de entrada da aplicação desktop. Coordena a inicialização
do sistema, autenticação do usuário e carregamento da interface principal.

Funcionalidades principais:
- Inicialização do banco de dados
- Tela de login segura
- Carregamento da interface principal com abas
- Controle de acesso baseado em nível de usuário
- Gerenciamento de tema visual moderno

Arquitetura da aplicação:
- Model-View-Controller implícito
- Interface baseada em abas (Notebook)
- Tema moderno com sv_ttk
- Controle de sessão de usuário

Fluxo de execução:
1. Inicializa banco de dados (init_db)
2. Exibe tela de login (login_screen)
3. Se autenticação ok, carrega aplicação principal (MainApp)
4. Se falha, encerra aplicação
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk  # Tema visual moderno para tkinter

from animals_tab import AnimalsTab
from adoptions_tab import AdoptionsTab
from users_tab import UsersTab
from shelter_tab import ShelterTab
from search_tab import SearchTab
from adm_tab import AdmTab
from database import init_db
from login import login_screen

class MainApp(tk.Tk):
    """
    Classe principal da aplicação desktop.
    
    Herda de tk.Tk e gerencia toda a interface do usuário,
    incluindo o notebook com abas e controle de acesso.
    
    Atributos:
        usuario_logado (AuthUser): Usuário autenticado
        notebook (ttk.Notebook): Container de abas principal
    """
    
    def __init__(self, usuario_logado=None):
        """
        Inicializa a aplicação principal.
        
        Args:
            usuario_logado (AuthUser): Usuário autenticado pela tela de login
            
        Configurações:
            - Título e geometria da janela
            - Tema visual sv_ttk moderno
            - Notebook como container principal
            - Abas baseadas no nível de acesso
        """
        super().__init__()
        
        # Configuração da janela principal
        self.title("Sistema de Gerenciamento de Abrigo Animal")
        self.geometry("1400x900")  # Tamanho maior para melhor experiência
        
        # Aplica o tema visual moderno sv_ttk
        sv_ttk.set_theme("light")  # Tema claro e moderno
        
        # Armazena o usuário logado para controle de acesso
        self.usuario_logado = usuario_logado
        
        # Cria o notebook (container de abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # ========== ABAS PADRÃO (ACESSO A TODOS) ==========
        
        # Aba de Animais - Gerenciamento completo
        animals_tab = AnimalsTab(self.notebook)
        self.notebook.add(animals_tab, text="Animais")
        
        # Aba de Adoções - Processos de adoção
        adoptions_tab = AdoptionsTab(self.notebook)
        self.notebook.add(adoptions_tab, text="Adoções")
        
        # Aba de Tutores - Usuários do sistema
        users_tab = UsersTab(self.notebook)
        self.notebook.add(users_tab, text="Tutores")
        
        # Aba de Abrigos - Gerenciamento de abrigos
        shelter_tab = ShelterTab(self.notebook)
        self.notebook.add(shelter_tab, text="Abrigos")
        
        # Aba de Pesquisa - Busca avançada
        search_tab = SearchTab(self.notebook)
        self.notebook.add(search_tab, text="Pesquisa")
        
        # ========== ABA ADMINISTRATIVA (SOMENTE ADMINS) ==========
        
        # Verifica se o usuário tem permissão de admin
        if usuario_logado and usuario_logado.is_admin():
            adm_tab = AdmTab(self.notebook, usuario_logado)
            self.notebook.add(adm_tab, text="Administração")
        
        # Personaliza o título com informações do usuário
        if usuario_logado:
            self.title(f"Sistema de Abrigo Animal - Usuário: {usuario_logado.username}")

if __name__ == "__main__":
    """
    Ponto de entrada da aplicação.
    
    Fluxo de execução:
    1. Inicializa o banco de dados (cria tabelas e dados padrão)
    2. Exibe a tela de login e tenta autenticar
    3. Se sucesso: inicia a aplicação principal com tema moderno
    4. Se falha: encerra com mensagem
    """
    
    # Inicialização do banco de dados
    print("Inicializando banco de dados...")
    init_db()
    
    # Tela de login
    print("Carregando tela de login...")
    usuario = login_screen()
    
    # Verificação de autenticação
    if usuario:
        # Login bem-sucedido - inicia aplicação principal com tema moderno
        print(f"Usuário {usuario.username} autenticado com sucesso!")
        print("Carregando interface com tema moderno...")
        app = MainApp(usuario)
        app.mainloop()
    else:
        # Login falhou ou foi cancelado
        print("Login falhou ou foi cancelado. Encerrando aplicação.")