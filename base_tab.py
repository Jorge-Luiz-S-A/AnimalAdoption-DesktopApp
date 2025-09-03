"""
Classe Base para Abas do Sistema
--------------------------------
Fornece funcionalidades comuns e estilos para todas as abas da aplicação.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class BaseTab(ttk.Frame):
    """
    Classe base para todas as abas do sistema.
    
    Fornece:
    - Estilos comuns para a interface
    - Métodos utilitários para exibição de mensagens
    - Método para criação de campos de formulário
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba base.
        
        Args:
            parent: Widget pai onde a aba será inserida
        """
        super().__init__(parent)
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Required.TLabel", foreground="red")
        self.style.configure("Success.TButton", foreground="green")

    def info(self, msg: str):
        """
        Exibe uma mensagem de informação.
        
        Args:
            msg (str): Mensagem a ser exibida
        """
        messagebox.showinfo("Info", msg)

    def error(self, msg: str):
        """
        Exibe uma mensagem de erro.
        
        Args:
            msg (str): Mensagem de erro a ser exibida
        """
        messagebox.showerror("Erro", msg)

    def create_form_field(self, parent, label, row, required=False, tooltip=None):
        """
        Cria um campo de formulário com label.
        
        Args:
            parent: Widget pai onde o campo será criado
            label (str): Texto do label
            row (int): Linha onde o campo será posicionado
            required (bool): Se o campo é obrigatório
            tooltip (str): Texto de tooltip (opcional)
            
        Returns:
            int: Próxima linha disponível
        """
        label_widget = ttk.Label(parent, text=label)
        if required:
            label_widget.configure(style="Required.TLabel")
        label_widget.grid(row=row, column=0, sticky="w", pady=(5, 2))
        return row + 1
