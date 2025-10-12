# main.py (atualizado)
"""
Aplicação principal com aba de animais
"""
import tkinter as tk
from tkinter import ttk
from animals_tab import AnimalsTab

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Abrigo Animal")
        self.geometry("800x600")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        # Adiciona aba de animais
        animals_tab = AnimalsTab(self.notebook)
        self.notebook.add(animals_tab, text="Animais")
        
        # Inicializa banco
        from database import init_db
        init_db()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()