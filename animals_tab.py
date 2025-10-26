# animals_tab.py (atualizado com utilitários)
"""
Aba de animais melhorada
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal, Shelter
from utils import SIZES, GENDERS, STATUSES, parse_int

class AnimalsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(self, text="Gerenciamento de Animais", font=("Arial", 14, "bold")).pack(pady=10)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista (esquerda)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Lista de Animais", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.tree = ttk.Treeview(left_frame, 
            columns=("ID", "Nome", "Espécie", "Idade", "Porte", "Status", "Abrigo"),
            show="headings", height=15)
        
        colunas = [
            ("ID", 50), ("Nome", 150), ("Espécie", 100), ("Idade", 60),
            ("Porte", 80), ("Status", 100), ("Abrigo", 120)
        ]
        
        for col, width in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário (direita)
        form_frame = ttk.Frame(main_frame, width=350)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Dados do Animal", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos com valores pré-definidos
        campos = [
            ("Nome *", ttk.Entry, {"width": 30}),
            ("Espécie", ttk.Combobox, {"values": ["Cachorro", "Gato", "Pássaro"], "state": "readonly", "width": 30}),
            ("Raça", ttk.Entry, {"width": 30}),
            ("Idade", ttk.Entry, {"width": 30}),
            ("Porte", ttk.Combobox, {"values": SIZES, "state": "readonly", "width": 30}),
            ("Gênero", ttk.Combobox, {"values": GENDERS, "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": STATUSES, "state": "readonly", "width": 30}),
        ]
        
        self.inputs = {}
        linha = 0
        for label, widget_class, opts in campos:
            ttk.Label(form_frame, text=label).grid(row=linha, column=0, sticky="w", pady=(5, 0))
            linha += 1
            
            widget = widget_class(form_frame, **opts)
            widget.grid(row=linha, column=0, sticky="we", pady=(0, 10))
            self.inputs[label] = widget
            linha += 1
        
        # Abrigo
        ttk.Label(form_frame, text="Abrigo").grid(row=linha, column=0, sticky="w", pady=(5, 0))
        linha += 1
        self.shelter_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.shelter_combo.grid(row=linha, column=0, sticky="we", pady=(0, 10))
        linha += 1
        
        # Observações
        ttk.Label(form_frame, text="Observações").grid(row=linha, column=0, sticky="w", pady=(5, 0))
        linha += 1
        self.notes_text = tk.Text(form_frame, height=4, width=30)
        self.notes_text.grid(row=linha, column=0, sticky="we", pady=(0, 10))
        linha += 1
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=linha, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.carregar_lista).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_lista()
    
    def carregar_abrigos(self):
        """Carrega lista de abrigos"""
        abrigos = session.query(Shelter).all()
        return [f"{s.id} - {s.name}" for s in abrigos]
    
    def carregar_lista(self):
        """Carrega animais na lista"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Atualiza combobox de abrigos
        self.shelter_combo['values'] = self.carregar_abrigos()
        
        animais = session.query(Animal).order_by(Animal.id.desc()).all()
        for animal in animais:
            abrigo_nome = animal.shelter.name if animal.shelter else ""
            self.tree.insert("", "end", iid=str(animal.id), values=(
                animal.id, animal.name, animal.species, animal.age,
                animal.size or "", animal.status, abrigo_nome
            ))
    
    def on_select(self, event):
        """Quando seleciona animal"""
        selection = self.tree.selection()
        if not selection:
            return
            
        self.selected_id = int(selection[0])
        animal = session.query(Animal).get(self.selected_id)
        
        # Preenche campos
        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, animal.name)
        
        self.inputs["Espécie"].set(animal.species or "")
        self.inputs["Raça"].delete(0, tk.END)
        self.inputs["Raça"].insert(0, animal.breed or "")
        
        self.inputs["Idade"].delete(0, tk.END)
        self.inputs["Idade"].insert(0, str(animal.age))
        
        self.inputs["Porte"].set(animal.size or "")
        self.inputs["Gênero"].set(animal.gender or "")
        self.inputs["Status"].set(animal.status or "")
        
        if animal.shelter:
            self.shelter_combo.set(f"{animal.shelter.id} - {animal.shelter.name}")
        else:
            self.shelter_combo.set("")
            
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", animal.health_history or "")
    
    def novo(self):
        """Novo animal"""
        self.selected_id = None
        for widget in self.inputs.values():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.shelter_combo.set("")
        self.notes_text.delete("1.0", tk.END)
        self.inputs["Idade"].insert(0, "0")
        self.inputs["Status"].set("Disponível")
    
    def salvar(self):
        """Salva animal"""
        nome = self.inputs["Nome *"].get().strip()
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
        
        # Processa abrigo
        abrigo_val = self.shelter_combo.get()
        shelter_id = None
        if abrigo_val:
            shelter_id = int(abrigo_val.split(" - ")[0])
        
        if self.selected_id:
            # Edição
            animal = session.query(Animal).get(self.selected_id)
        else:
            # Novo
            animal = Animal()
            session.add(animal)
        
        # Atualiza dados
        animal.name = nome
        animal.species = self.inputs["Espécie"].get()
        animal.breed = self.inputs["Raça"].get().strip() or None
        animal.age = parse_int(self.inputs["Idade"].get().strip(), 0)
        animal.size = self.inputs["Porte"].get()
        animal.gender = self.inputs["Gênero"].get()
        animal.status = self.inputs["Status"].get()
        animal.health_history = self.notes_text.get("1.0", tk.END).strip() or None
        animal.shelter_id = shelter_id
        
        session.commit()
        self.carregar_lista()
        self.novo()
        messagebox.showinfo("Sucesso", "Animal salvo!")
    
    def excluir(self):
        """Exclui animal"""
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