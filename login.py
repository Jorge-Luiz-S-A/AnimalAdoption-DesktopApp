# login.py
import tkinter as tk
from tkinter import messagebox
from database import session
from models import AuthUser

def login_screen():
    root = tk.Tk()
    root.title("Login - Animal Adoption")
    root.geometry("300x200")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Usuário:").pack(pady=5)
    username_entry = tk.Entry(root, width=20)
    username_entry.pack()
    username_entry.focus()

    tk.Label(root, text="Senha:").pack(pady=5)
    password_entry = tk.Entry(root, show="*", width=20)
    password_entry.pack()

    result = {"authenticated": False}

    def authenticate():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Erro", "Digite usuário e senha!")
            return
        user = session.query(AuthUser).filter_by(username=username).first()
        if user and user.check_password(password):
            result["authenticated"] = True
            root.destroy()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Entrar", command=authenticate, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancelar", command=root.destroy, width=10).pack(side=tk.LEFT, padx=5)

    root.bind('<Return>', lambda event: authenticate())
    root.mainloop()
    return result["authenticated"]
