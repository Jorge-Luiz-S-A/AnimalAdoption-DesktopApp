# login.py
"""
Sistema de login do sistema
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AuthUser

def login_screen():
    """Tela de login"""
    root = tk.Tk()
    root.title("Login - Sistema de Abrigo")
    root.geometry("350x200")
    root.resizable(False, False)
    
    # Centraliza na tela
    root.eval('tk::PlaceWindow . center')
    
    container = ttk.Frame(root, padding=20)
    container.pack(expand=True, fill="both")
    
    # Campos
    ttk.Label(container, text="Usuário:").grid(row=0, column=0, sticky="w", pady=(0, 5))
    username_entry = ttk.Entry(container, width=25)
    username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    username_entry.focus()
    
    ttk.Label(container, text="Senha:").grid(row=2, column=0, sticky="w", pady=(0, 5))
    password_entry = ttk.Entry(container, show="*", width=25)
    password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))
    
    resultado = {"usuario": None}
    
    def autenticar():
        """Verifica login"""
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erro", "Digite usuário e senha!")
            return
        
        # Busca usuário
        usuario = session.query(AuthUser).filter_by(username=username).first()
        
        if usuario and usuario.check_password(password):
            resultado["usuario"] = usuario
            root.destroy()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
    
    # Botões
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=4, column=0, pady=15)
    
    ttk.Button(btn_frame, text="Entrar", command=autenticar, width=12).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=root.destroy, width=12).pack(side=tk.LEFT, padx=5)
    
    # Enter para login
    root.bind('<Return>', lambda event: autenticar())
    
    root.mainloop()
    return resultado["usuario"]