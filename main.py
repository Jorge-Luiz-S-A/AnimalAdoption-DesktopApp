# main.py (com aba de pesquisa)
"""
App completo com todas as abas
"""
import tkinter as tk
from tkinter import ttk
from animals_tab import AnimalsTab
from adoptions_tab import AdoptionsTab
from users_tab import UsersTab
from shelter_tab import ShelterTab
from search_tab import SearchTab
from database import init_db
from login import login_screen

class MainApp(tk.Tk):
    def __init__(self, usuario_logado):
        super().__init__()
        self.title(f"Sistema de Abrigo Animal - Usuário: {usuario_logado.username}")
        self.geometry("1300x800")
        
        self.usuario_logado = usuario_logado
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        # Todas as abas principais
        animals_tab = AnimalsTab(self.notebook)
        self.notebook.add(animals_tab, text="Animais")
        
        adoptions_tab = AdoptionsTab(self.notebook)
        self.notebook.add(adoptions_tab, text="Adoções")
        
        users_tab = UsersTab(self.notebook)
        self.notebook.add(users_tab, text="Tutores")
        
        shelter_tab = ShelterTab(self.notebook)
        self.notebook.add(shelter_tab, text="Abrigos")
        
        search_tab = SearchTab(self.notebook)
        self.notebook.add(search_tab, text="Pesquisa")
        
        # Aba admin só para admins
        if usuario_logado.is_admin():
            from adm_tab import AdmTab
            adm_tab = AdmTab(self.notebook, usuario_logado)
            self.notebook.add(adm_tab, text="Administração")

if __name__ == "__main__":
    init_db()
    usuario = login_screen()
    
    if usuario:
        print(f"Usuário {usuario.username} autenticado!")
        app = MainApp(usuario)
        app.mainloop()
    else:
        print("Aplicação encerrada.")
