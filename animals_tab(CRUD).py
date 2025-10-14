# animals_tab.py (versão com CRUD completo)
"""
Aba de animais com operações completas
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal

class AnimalsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(self, text="Gerenciamento de Animais", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de animais (esquerda)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Lista de Animais", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Treeview para lista
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Nome", "Espécie", "Status"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Espécie", text="Espécie")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50)
        self.tree.column("Nome", width=150)
        self.tree.column("Espécie", width=100)
        self.tree.column("Status", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário (direita)
        form_frame = ttk.Frame(main_frame, width=300)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Dados do Animal", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos do formulário
        ttk.Label(form_frame, text="Nome:").pack(anchor=tk.W)
        self.nome_entry = ttk.Entry(form_frame, width=30)
        self.nome_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Espécie:").pack(anchor=tk.W)
        self.especie_combo = ttk.Combobox(form_frame, values=["Cachorro", "Gato", "Pássaro"], state="readonly", width=27)
        self.especie_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Idade:").pack(anchor=tk.W)
        self.idade_entry = ttk.Entry(form_frame, width=30)
        self.idade_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Status:").pack(anchor=tk.W)
        self.status_combo = ttk.Combobox(form_frame, values=["Disponível", "Adotado", "Em tratamento"], state="readonly", width=27)
        self.status_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_lista()
    
    def carregar_lista(self):
        """Carrega animais na lista"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        animais = session.query(Animal).all()
        for animal in animais:
            self.tree.insert("", "end", values=(animal.id, animal.name, animal.species, animal.status))
    
    def on_select(self, event):
        """Quando seleciona um animal na lista"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            
            # Busca animal no banco
            animal = session.query(Animal).get(self.selected_id)
            
            # Preenche formulário
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, animal.name)
            
            self.especie_combo.set(animal.species)
            
            self.idade_entry.delete(0, tk.END)
            self.idade_entry.insert(0, str(animal.age))
            
            self.status_combo.set(animal.status)
    
    def novo(self):
        """Prepara para novo animal"""
        self.selected_id = None
        self.nome_entry.delete(0, tk.END)
        self.especie_combo.set("")
        self.idade_entry.delete(0, tk.END)
        self.idade_entry.insert(0, "0")
        self.status_combo.set("Disponível")
    
    def salvar(self):
        """Salva animal no banco"""
        nome = self.nome_entry.get().strip()
        especie = self.especie_combo.get()
        idade = self.idade_entry.get().strip()
        status = self.status_combo.get()
        
        if not nome or not especie:
            messagebox.showerror("Erro", "Nome e espécie são obrigatórios!")
            return
        
        try:
            idade_int = int(idade)
        except:
            messagebox.showerror("Erro", "Idade deve ser um número!")
            return
        
        if self.selected_id:
            # Edição
            animal = session.query(Animal).get(self.selected_id)
            animal.name = nome
            animal.species = especie
            animal.age = idade_int
            animal.status = status
            mensagem = "Animal atualizado!"
        else:
            # Novo
            animal = Animal(name=nome, species=especie, age=idade_int, status=status)
            session.add(animal)
            mensagem = "Animal cadastrado!"
        
        session.commit()
        self.carregar_lista()
        self.novo()
        messagebox.showinfo("Sucesso", mensagem)
    
    def excluir(self):
        """Exclui animal selecionado"""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um animal!")
            return
            
        if messagebox.askyesno("Confirmar", "Excluir animal selecionado?"):
            animal = session.query(Animal).get(self.selected_id)
            session.delete(animal)
            session.commit()
            self.carregar_lista()
            self.novo()
            messagebox.showinfo("Sucesso", "Animal excluído!")
