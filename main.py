"""
Aplicação Principal - Sistema de Gerenciamento de Abrigo Animal
---------------------------------------------------------------
Interface principal do sistema com abas para todas as funcionalidades.
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk

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
    Classe principal da aplicação.
    
    Responsável por:
    - Inicializar a interface gráfica
    - Criar o notebook com todas as abas
    - Gerenciar o tema visual
    - Controlar acesso baseado no nível do usuário
    """
    
    def __init__(self, usuario_logado=None):
        """Inicializa a aplicação principal."""
        super().__init__()
        self.title("Animal Adoption Platform")
        self.geometry("1366x768")
        sv_ttk.set_theme("light")
        
        self.usuario_logado = usuario_logado
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Adiciona abas padrão (disponíveis para todos os usuários)
        self.notebook.add(AnimalsTab(self.notebook), text="Animais")
        self.notebook.add(AdoptionsTab(self.notebook), text="Adoções")
        self.notebook.add(UsersTab(self.notebook), text="Usuários")
        self.notebook.add(ShelterTab(self.notebook), text="Abrigos")
        self.notebook.add(SearchTab(self.notebook), text="Pesquisa")
        
        # Adiciona aba ADM apenas se usuário for admin
        if usuario_logado and usuario_logado.is_admin():
            self.notebook.add(AdmTab(self.notebook, usuario_logado), text="ADM")
        
        # Exibe nome do usuário logado no título
        if usuario_logado:
            self.title(f"Sistema de Abrigo Animal - Usuário: {usuario_logado.username}")

if __name__ == "__main__":
    init_db()
    usuario = login_screen()
    if usuario:
        app = MainApp(usuario)
        app.mainloop()
    else:
        print("Login falhou. Encerrando aplicação.")
