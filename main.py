# main.py (com nova aba)
"""
App com abas de animais e adoções
"""
import tkinter as tk
from tkinter import ttk
from animals_tab import AnimalsTab
from adoptions_tab import AdoptionsTab

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Abrigo Animal")
        self.geometry("1000x700")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        # Abas
        animals_tab = AnimalsTab(self.notebook)
        self.notebook.add(animals_tab, text="Animais")
        
        adoptions_tab = AdoptionsTab(self.notebook)
        self.notebook.add(adoptions_tab, text="Adoções")
        
        from database import init_db
        init_db()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
