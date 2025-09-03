"""
Tela de Login - Autenticação de usuários
----------------------------------------
Interface para autenticação de usuários no sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

from database import session
from models import AuthUser

def login_screen():
    """
    Exibe a tela de login para autenticação de usuários.
    
    Returns:
        AuthUser: Objeto do usuário autenticado ou None se falhar
    """
    root = tk.Tk()
    root.title("Login - Animal Adoption")
    root.geometry("400x250")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    # Aplica o mesmo tema usado no app principal
    sv_ttk.set_theme("light")

    # Frame central para organizar os widgets
    container = ttk.Frame(root, padding=20)
    container.pack(expand=True, fill="both")

    # Usuário
    ttk.Label(container, text="Usuário:").grid(row=0, column=0, sticky="w", pady=(0, 5))
    username_entry = ttk.Entry(container, width=30)
    username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    username_entry.focus()

    # Senha
    ttk.Label(container, text="Senha:").grid(row=2, column=0, sticky="w", pady=(0, 5))
    password_entry = ttk.Entry(container, show="*", width=30)
    password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

    result = {"usuario": None}

    def authenticate():
        """
        Autentica o usuário com as credenciais fornecidas.
        
        Verifica se o usuário existe e se a senha está correta.
        """
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Erro", "Digite usuário e senha!")
            return

        user = session.query(AuthUser).filter_by(username=username).first()
        if user and user.check_password(password):
            result["usuario"] = user  # Retorna o objeto usuário
            root.destroy()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    # Botões
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=4, column=0, pady=15)

    ttk.Button(btn_frame, text="Entrar", command=authenticate, width=12).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=root.destroy, width=12).pack(side=tk.LEFT, padx=5)

    # Atalho Enter para login
    root.bind('<Return>', lambda event: authenticate())

    root.mainloop()
    return result["usuario"]
