# shelter_tab.py
"""
Aba para gerenciar abrigos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Shelter, Animal

class ShelterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(self, text="Gerenciamento de Abrigos", font=("Arial", 14, "bold")).pack(pady=10)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de abrigos
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Lista de Abrigos", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Nome", "Capacidade", "Animais"), show="headings", height=15)
        for col, width in [("ID", 50), ("Nome", 200), ("Capacidade", 100), ("Animais", 100)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário
        form_frame = ttk.Frame(main_frame, width=300)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Dados do Abrigo", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos
        fields = [
            ("Nome:", "nome_entry"),
            ("Email:", "email_entry"),
            ("Telefone:", "phone_entry"), 
            ("Endereço:", "address_entry"),
            ("Capacidade:", "capacity_entry")
        ]
        
        self.inputs = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i*2, column=0, sticky="w", pady=(5, 0))
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i*2+1, column=0, sticky="we", pady=(0, 10))
            self.inputs[key] = entry
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=10, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_lista()
    
    def carregar_lista(self):
        """Carrega abrigos com estatísticas"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        abrigos = session.query(Shelter).all()
        for shelter in abrigos:
            # Conta animais no abrigo
            animais_count = session.query(Animal).filter(Animal.shelter_id == shelter.id).count()
            
            self.tree.insert("", "end", values=(
                shelter.id, shelter.name or "", shelter.capacity or 0, animais_count
            ))
    
    def on_select(self, event):
        """Quando seleciona um abrigo"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            
            shelter = session.query(Shelter).get(self.selected_id)
            
            # Preenche campos
            self.inputs["nome_entry"].delete(0, tk.END)
            self.inputs["nome_entry"].insert(0, shelter.name or "")
            
            self.inputs["email_entry"].delete(0, tk.END)
            self.inputs["email_entry"].insert(0, shelter.email or "")
            
            self.inputs["phone_entry"].delete(0, tk.END)
            self.inputs["phone_entry"].insert(0, shelter.phone or "")
            
            self.inputs["address_entry"].delete(0, tk.END)
            self.inputs["address_entry"].insert(0, shelter.address or "")
            
            self.inputs["capacity_entry"].delete(0, tk.END)
            self.inputs["capacity_entry"].insert(0, str(shelter.capacity or 0))
    
    def novo(self):
        """Novo abrigo"""
        self.selected_id = None
        for entry in self.inputs.values():
            entry.delete(0, tk.END)
    
    def salvar(self):
        """Salva abrigo"""
        nome = self.inputs["nome_entry"].get().strip()
        capacidade = self.inputs["capacity_entry"].get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
        
        try:
            capacidade_int = int(capacidade) if capacidade else 0
        except:
            messagebox.showerror("Erro", "Capacidade deve ser um número!")
            return
        
        if self.selected_id:
            # Edição
            shelter = session.query(Shelter).get(self.selected_id)
            shelter.name = nome
            shelter.email = self.inputs["email_entry"].get().strip() or None
            shelter.phone = self.inputs["phone_entry"].get().strip() or None
            shelter.address = self.inputs["address_entry"].get().strip() or None
            shelter.capacity = capacidade_int
            mensagem = "Abrigo atualizado!"
        else:
            # Novo
            shelter = Shelter(
                name=nome,
                email=self.inputs["email_entry"].get().strip() or None,
                phone=self.inputs["phone_entry"].get().strip() or None,
                address=self.inputs["address_entry"].get().strip() or None,
                capacity=capacidade_int
            )
            session.add(shelter)
            mensagem = "Abrigo cadastrado!"
        
        session.commit()
        self.carregar_lista()
        self.novo()
        messagebox.showinfo("Sucesso", mensagem)
    
    def excluir(self):
        """Exclui abrigo"""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um abrigo!")
            return
            
        # Verifica se há animais no abrigo
        animais_count = session.query(Animal).filter(Animal.shelter_id == self.selected_id).count()
        if animais_count > 0:
            messagebox.showerror("Erro", f"Não é possível excluir! Existem {animais_count} animais neste abrigo.")
            return
            
        if messagebox.askyesno("Confirmar", "Excluir abrigo selecionado?"):
            shelter = session.query(Shelter).get(self.selected_id)
            session.delete(shelter)
            session.commit()
            self.carregar_lista()
            self.novo()
            messagebox.showinfo("Sucesso", "Abrigo excluído!")
