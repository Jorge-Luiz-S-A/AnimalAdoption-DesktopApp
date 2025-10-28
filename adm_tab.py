# adm_tab.py
"""
Aba de administração do sistema
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AuthUser

class AdmTab(ttk.Frame):
    def __init__(self, parent, usuario_logado):
        super().__init__(parent)
        
        self.usuario_logado = usuario_logado
        
        # Verifica se é admin
        if not usuario_logado.is_admin():
            self.mostrar_acesso_negado()
            return
        
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.criar_interface()
    
    def mostrar_acesso_negado(self):
        """Mostra mensagem de acesso negado"""
        label = ttk.Label(self, text="⛔ Acesso restrito a administradores", 
                         font=("Arial", 12, "bold"), foreground="red")
        label.pack(expand=True, pady=50)
    
    def criar_interface(self):
        """Cria interface da aba admin"""
        ttk.Label(self, text="Gerenciamento de Usuários do Sistema", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de usuários (esquerda)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Usuários do Sistema", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Usuário", "Nível Acesso"), show="headings", height=15)
        
        for col, width in [("ID", 50), ("Usuário", 150), ("Nível Acesso", 120)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(left_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário (direita)
        form_frame = ttk.Frame(main_frame, width=300)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Cadastrar/Editar Usuário", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos do formulário
        ttk.Label(form_frame, text="Usuário *").pack(anchor=tk.W, pady=(5, 0))
        self.usuario_entry = ttk.Entry(form_frame, width=25)
        self.usuario_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Senha *").pack(anchor=tk.W, pady=(5, 0))
        self.senha_entry = ttk.Entry(form_frame, show="*", width=25)
        self.senha_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Confirmar Senha *").pack(anchor=tk.W, pady=(5, 0))
        self.confirmar_senha_entry = ttk.Entry(form_frame, show="*", width=25)
        self.confirmar_senha_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Nível de Acesso *").pack(anchor=tk.W, pady=(5, 0))
        self.nivel_combo = ttk.Combobox(form_frame, values=["admin", "gestor", "usuario"], state="readonly", width=22)
        self.nivel_combo.pack(fill=tk.X, pady=(0, 15))
        self.nivel_combo.set("usuario")
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_usuarios()
    
    def carregar_usuarios(self):
        """Carrega lista de usuários"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        usuarios = session.query(AuthUser).order_by(AuthUser.username).all()
        for usuario in usuarios:
            self.tree.insert("", "end", iid=str(usuario.id),
                           values=(usuario.id, usuario.username, usuario.nivel_acesso))
    
    def on_select(self, event):
        """Quando seleciona usuário"""
        selection = self.tree.selection()
        if not selection:
            return
            
        self.selected_id = int(selection[0])
        usuario = session.query(AuthUser).get(self.selected_id)
        
        self.usuario_entry.delete(0, tk.END)
        self.usuario_entry.insert(0, usuario.username)
        
        self.nivel_combo.set(usuario.nivel_acesso)
        
        # Limpa senhas por segurança
        self.senha_entry.delete(0, tk.END)
        self.confirmar_senha_entry.delete(0, tk.END)
    
    def novo(self):
        """Prepara para novo usuário"""
        self.selected_id = None
        self.usuario_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.confirmar_senha_entry.delete(0, tk.END)
        self.nivel_combo.set("usuario")
    
    def salvar(self):
        """Salva usuário"""
        username = self.usuario_entry.get().strip()
        password = self.senha_entry.get().strip()
        confirmar_password = self.confirmar_senha_entry.get().strip()
        nivel_acesso = self.nivel_combo.get()
        
        # Validações
        if not username:
            messagebox.showerror("Erro", "Usuário é obrigatório.")
            return
            
        if not self.selected_id and (not password or not confirmar_password):
            messagebox.showerror("Erro", "Senha é obrigatória para novo usuário.")
            return
            
        if password != confirmar_password:
            messagebox.showerror("Erro", "Senhas não coincidem.")
            return
        
        if self.selected_id:
            # Edição
            usuario = session.query(AuthUser).get(self.selected_id)
            usuario.username = username
            usuario.nivel_acesso = nivel_acesso
            
            # Atualiza senha apenas se informada
            if password:
                usuario.set_password(password)
                
            mensagem = "Usuário atualizado com sucesso!"
        else:
            # Novo usuário
            if session.query(AuthUser).filter_by(username=username).first():
                messagebox.showerror("Erro", "Usuário já existe.")
                return
                
            usuario = AuthUser(username=username, nivel_acesso=nivel_acesso)
            usuario.set_password(password)
            session.add(usuario)
            mensagem = "Usuário criado com sucesso!"
        
        try:
            session.commit()
            self.carregar_usuarios()
            self.novo()
            messagebox.showinfo("Sucesso", mensagem)
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")
    
    def excluir(self):
        """Exclui usuário"""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um usuário.")
            return
            
        usuario = session.query(AuthUser).get(self.selected_id)
        
        # Impede auto-exclusão
        if usuario.id == self.usuario_logado.id:
            messagebox.showerror("Erro", "Você não pode excluir seu próprio usuário.")
            return
            
        if not messagebox.askyesno("Confirmar", f"Excluir usuário '{usuario.username}'?"):
            return
            
        try:
            session.delete(usuario)
            session.commit()
            self.carregar_usuarios()
            self.novo()
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}")
