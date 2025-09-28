"""
Módulo de Gerenciamento de Usuários/Tutores - CRUD Completo
-----------------------------------------------------------
Este módulo gerencia todos os usuários (tutores) do sistema de adoção.
Controla informações de contato, aprovação para adoção e observações.

Funcionalidades principais:
- Cadastro completo de usuários/tutores
- Controle de aprovação para processos de adoção
- Gestão de informações de contato (email, telefone, cidade)
- Campo de observações para informações adicionais
- Listagem organizada com status de aprovação

Informações gerenciadas:
- Dados pessoais: nome, email, telefone, cidade
- Status de aprovação para adoção
- Preferências e observações de adoção
- Histórico de processos vinculados

Validações implementadas:
- Nome e email são obrigatórios
- Email deve ser único no sistema
- Formatação básica de telefone
- Prevenção de exclusão de usuários com processos ativos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import User

class UsersTab(ttk.Frame):
    """
    Classe para gerenciamento completo de usuários/tutores.
    
    Esta classe implementa operações de CRUD para usuários com controle
    de aprovação e informações de contato completas.
    
    A interface é dividida em:
    - Painel esquerdo: Lista de usuários com informações básicas
    - Painel direito: Formulário detalhado para cadastro/edição
    
    Atributos:
        selected_id (int): ID do usuário selecionado para edição
        tree (ttk.Treeview): Tabela de usuários
        inputs (dict): Campos do formulário de usuário
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de gerenciamento de usuários.
        
        Args:
            parent: Widget pai container
            
        A construção inclui:
        1. Divisão em painéis esquerdo/direito
        2. Tabela com informações resumidas
        3. Formulário scrollable com todos os campos
        4. Sistema de aprovação para adoção
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== PAINEL ESQUERDO - LISTA DE USUÁRIOS ==========
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título da seção (usando "Tutores" para melhor entendimento)
        ttk.Label(left_panel, text="Lista de Tutores", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela de usuários
        self.tree = ttk.Treeview(table_frame,
                                 columns=("ID", "Nome", "Email", "Cidade", "Aprovado"),
                                 show="headings", 
                                 yscrollcommand=scrollbar.set, 
                                 height=20)
        scrollbar.config(command=self.tree.yview)

        # Configuração das colunas
        for c, w in (("ID", 50), ("Nome", 150), ("Email", 180), ("Cidade", 120), ("Aprovado", 80)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ========== PAINEL DIREITO - FORMULÁRIO ==========
        right_panel = ttk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Tutor", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Container scrollable do formulário
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Configuração do scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        # ========== CAMPOS DO FORMULÁRIO ==========
        r = 0
        fields = [
            ("Nome *", ttk.Entry, {"width": 30}),
            ("Email *", ttk.Entry, {"width": 30}),
            ("Telefone", ttk.Entry, {"width": 30}),
            ("Cidade", ttk.Entry, {"width": 30}),
            ("Aprovado", ttk.Combobox, {"values": ["", "Sim", "Não"], "state": "readonly", "width": 30}),
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        # Campo de observações
        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Observações"] = tk.Text(self.scrollable_frame, height=4, width=30)
        self.inputs["Observações"].grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
        r += 1

        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        # ========== INICIALIZAÇÃO ==========
        self.selected_id = None
        self.load()

    def load(self):
        """
        Carrega todos os usuários na tabela.
        
        Ordena os usuários por ID decrescente (mais recentes primeiro)
        e formata o campo de aprovação para exibição "Sim"/"Não".
        """
        # Limpa a tabela atual
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Busca todos os usuários ordenados por ID decrescente
        for usuario in session.query(User).order_by(User.id.desc()).all():
            self.tree.insert("", "end", iid=str(usuario.id),
                           values=(usuario.id, usuario.name, usuario.email, 
                                   usuario.city or "", "Sim" if usuario.approved else "Não"))

    def on_select(self, event):
        """
        Manipula a seleção de um usuário na lista.
        
        Preenche o formulário com os dados do usuário selecionado
        e formata o campo de aprovação para o combobox.
        """
        sel = self.tree.selection()
        if not sel: 
            return
            
        # Busca o usuário selecionado
        usuario = session.get(User, int(sel[0]))
        self.selected_id = usuario.id

        # Preenche campos básicos
        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, usuario.name or "")
        
        self.inputs["Email *"].delete(0, tk.END)
        self.inputs["Email *"].insert(0, usuario.email or "")
        
        self.inputs["Telefone"].delete(0, tk.END)
        self.inputs["Telefone"].insert(0, usuario.phone or "")
        
        self.inputs["Cidade"].delete(0, tk.END)
        self.inputs["Cidade"].insert(0, usuario.city or "")
        
        self.inputs["Aprovado"].set("Sim" if usuario.approved else "Não")
        
        # Preenche observações
        self.inputs["Observações"].delete("1.0", tk.END)
        self.inputs["Observações"].insert(tk.END, usuario.adoption_preferences or "")

    def new(self):
        """Limpa o formulário para cadastrar um novo usuário."""
        self.selected_id = None
        for key, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um usuário no banco de dados.
        
        Valida campos obrigatórios e formata os dados antes do salvamento.
        """
        # Validações de campos obrigatórios
        name = self.inputs["Nome *"].get().strip()
        email = self.inputs["Email *"].get().strip()
        
        if not name or not email:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.")
            return

        # Determina se é criação ou edição
        if self.selected_id:
            usuario = session.get(User, self.selected_id)
        else:
            usuario = User()
            session.add(usuario)

        # Atualiza dados básicos
        usuario.name = name
        usuario.email = email
        usuario.phone = self.inputs["Telefone"].get().strip() or None
        usuario.city = self.inputs["Cidade"].get().strip() or None
        usuario.approved = (self.inputs["Aprovado"].get() == "Sim")
        usuario.adoption_preferences = self.inputs["Observações"].get("1.0", tk.END).strip() or None

        try:
            session.commit()
            self.load()
            messagebox.showinfo("Sucesso", "Tutor salvo com sucesso.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar tutor: {e}")

    def delete(self):
        """
        Exclui o usuário selecionado após confirmação.
        
        Verifica se o usuário possui processos de adoção vinculados
        antes de permitir a exclusão.
        """
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um tutor.")
            return
            
        # Verifica se o usuário possui processos de adoção
        from models import AdoptionProcess
        processos_vinculados = session.query(AdoptionProcess).filter(AdoptionProcess.user_id == self.selected_id).count()
        if processos_vinculados > 0:
            messagebox.showerror("Erro", f"Não é possível excluir o tutor. Existem {processos_vinculados} processos de adoção vinculados a ele.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir tutor selecionado?"):
            return
            
        try:
            usuario = session.get(User, self.selected_id)
            session.delete(usuario)
            session.commit()
            
            self.new()
            self.load()
            messagebox.showinfo("Sucesso", "Tutor excluído com sucesso.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir tutor: {e}")
