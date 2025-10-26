# base_tab.py
"""
Classe base para todas as abas
"""
import tkinter as tk
from tkinter import ttk, messagebox

class BaseTab(ttk.Frame):
    """Classe base com funcionalidades comuns"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.style = ttk.Style()
        
        # Configura estilos
        self.style.configure("Header.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Success.TButton", foreground="green")
    
    def info(self, mensagem):
        """Mostra mensagem de informação"""
        messagebox.showinfo("Informação", mensagem)
    
    def erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)