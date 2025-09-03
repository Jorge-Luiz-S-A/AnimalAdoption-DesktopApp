"""
Aba ADM - Gerenciamento de Usuários do Sistema
----------------------------------------------
Aba exclusiva para administradores gerenciarem usuários do sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AuthUser

class AdmTab(ttk.Frame):
    """
    Aba para gerenciamento de usuários do sistema.
    Acessível apenas para usuários com nível de acesso 'admin'.
    """
    
    def __init__(self, parent, usuario_logado=None):
        """
        Inicializa a aba ADM.
        
        Args:
            parent: Widget pai
            usuario_logado: Objeto AuthUser do usuário logado
        """
        super().__init__(parent)
        
        # Verifica se usuário tem permissão de admin
        self.usuario_logado = usuario_logado
        if not usuario_logado or not usuario_logado.is_admin():
            self.mostrar_acesso_negado()
            return
            
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.criar_interface()
        
    def mostrar_acesso_negado(self):
        """Exibe mensagem de acesso negado para não administradores."""
        label = ttk.Label(self, text="⛔ Acesso restrito a administradores", 
                         font=("Arial", 12, "bold"), foreground="red")
        label.pack(expand=True, pady=50)
        
    def criar_interface(self):
        """Cria a interface de gerenciamento de usuários."""
        # Título
        ttk.Label(self, text="Gerenciamento de Usuários do Sistema", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Lista de usuários
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="Usuários do Sistema", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Tabela de usuários
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Usuário", "Nível Acesso"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.tree.yview)
        
        for col, width in [("ID", 50), ("Usuário", 150), ("Nível Acesso", 120)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, anchor=tk.W)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right panel - Formulário
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        ttk.Label(right_panel, text="Cadastrar/Editar Usuário", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Formulário
        form_frame = ttk.Frame(right_panel)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        ttk.Label(form_frame, text="Usuário *").grid(row=0, column=0, sticky="w", pady=(5, 2))
        self.entry_usuario = ttk.Entry(form_frame, width=25)
        self.entry_usuario.grid(row=1, column=0, sticky="we", pady=(0, 10))
        
        ttk.Label(form_frame, text="Senha *").grid(row=2, column=0, sticky="w", pady=(5, 2))
        self.entry_senha = ttk.Entry(form_frame, width=25, show="*")
        self.entry_senha.grid(row=3, column=0, sticky="we", pady=(0, 10))
        
        ttk.Label(form_frame, text="Confirmar Senha *").grid(row=4, column=0, sticky="w", pady=(5, 2))
        self.entry_confirmar_senha = ttk.Entry(form_frame, width=25, show="*")
        self.entry_confirmar_senha.grid(row=5, column=0, sticky="we", pady=(0, 10))
        
        ttk.Label(form_frame, text="Nível de Acesso *").grid(row=6, column=0, sticky="w", pady=(5, 2))
        self.combo_nivel = ttk.Combobox(form_frame, values=["admin", "gestor", "usuario"], 
                                      state="readonly", width=22)
        self.combo_nivel.grid(row=7, column=0, sticky="we", pady=(0, 15))
        self.combo_nivel.set("usuario")
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir_usuario).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_usuarios()
    
    def carregar_usuarios(self):
        """Carrega todos os usuários na lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        usuarios = session.query(AuthUser).order_by(AuthUser.username).all()
        for usuario in usuarios:
            self.tree.insert("", "end", iid=str(usuario.id),
                           values=(usuario.id, usuario.username, usuario.nivel_acesso))
    
    def on_select(self, event):
        """Carrega o usuário selecionado para edição."""
        selecionados = self.tree.selection()
        if not selecionados:
            return
            
        usuario_id = int(selecionados[0])
        usuario = session.query(AuthUser).get(usuario_id)
        self.selected_id = usuario.id
        
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, usuario.username)
        self.combo_nivel.set(usuario.nivel_acesso)
        
        # Limpa campos de senha para segurança
        self.entry_senha.delete(0, tk.END)
        self.entry_confirmar_senha.delete(0, tk.END)
    
    def novo_usuario(self):
        """Prepara o formulário para novo usuário."""
        self.selected_id = None
        self.entry_usuario.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)
        self.entry_confirmar_senha.delete(0, tk.END)
        self.combo_nivel.set("usuario")
    
    def salvar_usuario(self):
        """Salva ou atualiza um usuário."""
        username = self.entry_usuario.get().strip()
        password = self.entry_senha.get().strip()
        confirmar_password = self.entry_confirmar_senha.get().strip()
        nivel_acesso = self.combo_nivel.get()
        
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
            # Edição de usuário existente
            usuario = session.query(AuthUser).get(self.selected_id)
            usuario.username = username
            usuario.nivel_acesso = nivel_acesso
            
            # Atualiza senha apenas se foi informada
            if password:
                usuario.set_password(password)
                
            message = "Usuário atualizado com sucesso!"
        else:
            # Novo usuário
            if session.query(AuthUser).filter_by(username=username).first():
                messagebox.showerror("Erro", "Usuário já existe.")
                return
                
            usuario = AuthUser(username=username, nivel_acesso=nivel_acesso)
            usuario.set_password(password)
            session.add(usuario)
            message = "Usuário criado com sucesso!"
        
        try:
            session.commit()
            self.carregar_usuarios()
            self.novo_usuario()
            messagebox.showinfo("Sucesso", message)
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado."""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um usuário para excluir.")
            return
            
        usuario = session.query(AuthUser).get(self.selected_id)
        
        # Impede a exclusão do próprio usuário logado
        if usuario.id == self.usuario_logado.id:
            messagebox.showerror("Erro", "Você não pode excluir seu próprio usuário.")
            return
            
        if not messagebox.askyesno("Confirmar", f"Excluir usuário '{usuario.username}'?"):
            return
            
        try:
            session.delete(usuario)
            session.commit()
            self.carregar_usuarios()
            self.novo_usuario()
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}")
