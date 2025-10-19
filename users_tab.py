# users_tab.py
"""
Aba para gerenciar usuários/tutores
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import User

class UsersTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(self, text="Gerenciamento de Tutores", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de usuários
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Lista de Tutores", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Nome", "Email", "Cidade", "Aprovado"), show="headings", height=15)
        columns_config = [("ID", 50), ("Nome", 150), ("Email", 180), ("Cidade", 120), ("Aprovado", 80)]
        for col, width in columns_config:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário
        form_frame = ttk.Frame(main_frame, width=300)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Dados do Tutor", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos
        fields = [
            ("Nome:", "nome_entry"),
            ("Email:", "email_entry"), 
            ("Telefone:", "phone_entry"),
            ("Cidade:", "city_entry")
        ]
        
        self.inputs = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i*2, column=0, sticky="w", pady=(5, 0))
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i*2+1, column=0, sticky="we", pady=(0, 10))
            self.inputs[key] = entry
        
        # Aprovado
        ttk.Label(form_frame, text="Aprovado:").grid(row=8, column=0, sticky="w", pady=(5, 0))
        self.approved_combo = ttk.Combobox(form_frame, values=["Sim", "Não"], state="readonly", width=27)
        self.approved_combo.grid(row=9, column=0, sticky="we", pady=(0, 10))
        
        # Observações
        ttk.Label(form_frame, text="Observações:").grid(row=10, column=0, sticky="w", pady=(5, 0))
        self.notes_text = tk.Text(form_frame, height=4, width=30)
        self.notes_text.grid(row=11, column=0, sticky="we", pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=12, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_lista()
    
    def carregar_lista(self):
        """Carrega usuários na lista"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        usuarios = session.query(User).all()
        for user in usuarios:
            self.tree.insert("", "end", values=(
                user.id, user.name, user.email or "", 
                user.city or "", "Sim" if user.approved else "Não"
            ))
    
    def on_select(self, event):
        """Quando seleciona um usuário"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            
            user = session.query(User).get(self.selected_id)
            
            # Preenche campos
            self.inputs["nome_entry"].delete(0, tk.END)
            self.inputs["nome_entry"].insert(0, user.name)
            
            self.inputs["email_entry"].delete(0, tk.END)
            self.inputs["email_entry"].insert(0, user.email or "")
            
            self.inputs["phone_entry"].delete(0, tk.END)
            self.inputs["phone_entry"].insert(0, user.phone or "")
            
            self.inputs["city_entry"].delete(0, tk.END)
            self.inputs["city_entry"].insert(0, user.city or "")
            
            self.approved_combo.set("Sim" if user.approved else "Não")
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", user.adoption_preferences or "")
    
    def novo(self):
        """Novo usuário"""
        self.selected_id = None
        for entry in self.inputs.values():
            entry.delete(0, tk.END)
        self.approved_combo.set("Não")
        self.notes_text.delete("1.0", tk.END)
    
    def salvar(self):
        """Salva usuário"""
        nome = self.inputs["nome_entry"].get().strip()
        email = self.inputs["email_entry"].get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
        
        if self.selected_id:
            # Edição
            user = session.query(User).get(self.selected_id)
            user.name = nome
            user.email = email
            user.phone = self.inputs["phone_entry"].get().strip() or None
            user.city = self.inputs["city_entry"].get().strip() or None
            user.approved = (self.approved_combo.get() == "Sim")
            user.adoption_preferences = self.notes_text.get("1.0", tk.END).strip() or None
            mensagem = "Tutor atualizado!"
        else:
            # Novo
            user = User(
                name=nome,
                email=email or None,
                phone=self.inputs["phone_entry"].get().strip() or None,
                city=self.inputs["city_entry"].get().strip() or None,
                approved=(self.approved_combo.get() == "Sim"),
                adoption_preferences=self.notes_text.get("1.0", tk.END).strip() or None
            )
            session.add(user)
            mensagem = "Tutor cadastrado!"
        
        session.commit()
        self.carregar_lista()
        self.novo()
        messagebox.showinfo("Sucesso", mensagem)
    
    def excluir(self):
        """Exclui usuário"""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um tutor!")
            return
            
        if messagebox.askyesno("Confirmar", "Excluir tutor selecionado?"):
            user = session.query(User).get(self.selected_id)
            session.delete(user)
            session.commit()
            self.carregar_lista()
            self.novo()
            messagebox.showinfo("Sucesso", "Tutor excluído!")
