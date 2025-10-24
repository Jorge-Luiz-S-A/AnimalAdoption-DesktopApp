# main.py (com sistema de login)
"""
App com login e controle de acesso
"""
import tkinter as tk
from tkinter import ttk
from animals_tab import AnimalsTab
from adoptions_tab import AdoptionsTab
from users_tab import UsersTab
from shelter_tab import ShelterTab
from database import init_db
from login import login_screen

class MainApp(tk.Tk):
    def __init__(self, usuario_logado):
        super().__init__()
        self.title(f"Sistema de Abrigo - Usuário: {usuario_logado.username}")
        self.geometry("1200x800")
        
        self.usuario_logado = usuario_logado
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        # Abas disponíveis para todos
        animals_tab = AnimalsTab(self.notebook)
        self.notebook.add(animals_tab, text="Animais")
        
        adoptions_tab = AdoptionsTab(self.notebook)
        self.notebook.add(adoptions_tab, text="Adoções")
        
        users_tab = UsersTab(self.notebook)
        self.notebook.add(users_tab, text="Tutores")
        
        shelter_tab = ShelterTab(self.notebook)
        self.notebook.add(shelter_tab, text="Abrigos")
        
        # Aba admin só para administradores
        if usuario_logado.is_admin():
            from adm_tab import AdmTab
            adm_tab = AdmTab(self.notebook, usuario_logado)
            self.notebook.add(adm_tab, text="Administração")

if __name__ == "__main__":
    # Inicializa banco
    init_db()
    
    # Tela de login
    usuario = login_screen()
    
    if usuario:
        print(f"Bem-vindo, {usuario.username}!")
        app = MainApp(usuario)
        app.mainloop()
    else:
        print("Login cancelado ou falhou.")