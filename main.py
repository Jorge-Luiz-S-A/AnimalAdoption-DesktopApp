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
from database import init_db
from login import login_screen

class MainApp(tk.Tk):
    """
    Classe principal da aplicação.
    
    Responsável por:
    - Inicializar a interface gráfica
    - Criar o notebook com todas as abas
    - Gerenciar o tema visual
    """
    
    def __init__(self):
        """Inicializa a aplicação principal."""
        super().__init__()
        self.title("Animal Adoption Platform")
        self.geometry("1600x900")
        sv_ttk.set_theme("light")

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        notebook.add(AnimalsTab(notebook), text="Animals")
        notebook.add(AdoptionsTab(notebook), text="Adoptions")
        notebook.add(UsersTab(notebook), text="Users")
        notebook.add(ShelterTab(notebook), text="Shelter")
        notebook.add(SearchTab(notebook), text="Search")

if __name__ == "__main__":
    # Inicializa o banco de dados
    init_db()
    
    # Exibe tela de login e inicia aplicação se autenticação for bem-sucedida
    if login_screen():
        app = MainApp()
        app.mainloop()
    else:
        print("Login falhou. Encerrando aplicação.")
