"""
Aba de Usuários - CRUD completo
-------------------------------
Gerencia todos os usuários do sistema com formulário completo.
Inclui campo de observações para informações adicionais.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import User

class UsersTab(ttk.Frame):
    """
    Aba para gerenciamento de usuários.
    
    Funcionalidades:
    - Listar todos os usuários
    - Criar, editar e excluir usuários
    - Gerenciar aprovação de usuários para adoção
    - Campo de observações para informações adicionais
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de usuários.
        
        Args:
            parent: Widget pai onde a aba será inserida
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -------- Left panel: Lista de usuários --------
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Lista de Tutores", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame,
                                 columns=("ID","Nome","Email","Cidade","Aprovado"),
                                 show="headings", yscrollcommand=scrollbar.set, height=20)
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID",50),("Nome",150),("Email",180),("Cidade",120),("Aprovado",80)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # -------- Right panel: Formulário --------
        right_panel = ttk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Tutor", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,10))

        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        # Campos do formulário (Label acima do input)
        r = 0
        fields = [
            ("Nome *", ttk.Entry, {"width":30}),
            ("Email *", ttk.Entry, {"width":30}),
            ("Telefone", ttk.Entry, {"width":30}),
            ("Cidade", ttk.Entry, {"width":30}),
            ("Aprovado", ttk.Combobox, {"values":["","Sim","Não"], "state":"readonly", "width":30}),
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5,0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0,5))
            self.inputs[label_text] = w
            r += 1

        # Campo Observações (igual ao formulário de animais)
        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r, column=0, columnspan=2, sticky="w", pady=(5,0))
        r += 1
        self.inputs["Observações"] = tk.Text(self.scrollable_frame, height=4, width=30)
        self.inputs["Observações"].grid(row=r, column=0, columnspan=2, sticky="we", pady=(0,5))
        r += 1

        # Botões
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()

    # ---------------- Funções ----------------
    def load(self):
        """Carrega todos os usuários na lista."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for u in session.query(User).order_by(User.id.desc()).all():
            self.tree.insert("", "end", iid=str(u.id),
                             values=(u.id, u.name, u.email, u.city or "", "Sim" if u.approved else "Não"))

    def on_select(self, event):
        """
        Manipula a seleção de um usuário na lista.
        
        Args:
            event: Evento de seleção da Treeview
        """
        sel = self.tree.selection()
        if not sel: 
            return
            
        u = session.get(User, int(sel[0]))
        self.selected_id = u.id

        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, u.name or "")
        self.inputs["Email *"].delete(0, tk.END)
        self.inputs["Email *"].insert(0, u.email or "")
        self.inputs["Telefone"].delete(0, tk.END)
        self.inputs["Telefone"].insert(0, u.phone or "")
        self.inputs["Cidade"].delete(0, tk.END)
        self.inputs["Cidade"].insert(0, u.city or "")
        self.inputs["Aprovado"].set("Sim" if u.approved else "Não")
        
        # Campo Observações
        self.inputs["Observações"].delete("1.0", tk.END)
        self.inputs["Observações"].insert(tk.END, u.adoption_preferences or "")

    def new(self):
        """Limpa o formulário para criar um novo usuário."""
        self.selected_id = None
        for key, w in self.inputs.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            elif isinstance(w, tk.Text):
                w.delete("1.0", tk.END)
            else:
                w.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um usuário.
        
        Valida se nome e email foram preenchidos.
        """
        name = self.inputs["Nome *"].get().strip()
        email = self.inputs["Email *"].get().strip()
        if not name or not email:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.")
            return

        if self.selected_id:
            u = session.get(User, self.selected_id)
        else:
            u = User()
            session.add(u)

        u.name = name
        u.email = email
        u.phone = self.inputs["Telefone"].get().strip() or None
        u.city = self.inputs["Cidade"].get().strip() or None
        u.approved = (self.inputs["Aprovado"].get() == "Sim")
        u.adoption_preferences = self.inputs["Observações"].get("1.0", tk.END).strip() or None

        session.commit()
        self.load()
        messagebox.showinfo("Sucesso", "Tutor salvo com sucesso.")

    def delete(self):
        """Exclui o usuário selecionado após confirmação."""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um tutor.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir tutor selecionado?"):
            return
        u = session.get(User, self.selected_id)
        session.delete(u)
        session.commit()
        self.new()
        self.load()
        messagebox.showinfo("Sucesso", "Tutor excluído com sucesso.")
