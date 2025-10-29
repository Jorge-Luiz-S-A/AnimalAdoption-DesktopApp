import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal, AdoptionProcess, Shelter
from utils import SIZES, GENDERS, parse_int

class AnimalsTab(ttk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(left_panel, text="Lista de Animais", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "Espécie", "Raça", "Idade", "Porte", "Gênero", "Status", "Abrigo"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        
        scrollbar.config(command=self.tree.yview)

        columns_config = [
            ("ID", 50), ("Nome", 140), ("Espécie", 100), ("Raça", 120), 
            ("Idade", 60), ("Porte", 80), ("Gênero", 80), ("Status", 100), ("Abrigo", 120)
        ]
        
        for column_name, width in columns_config:
            self.tree.heading(column_name, text=column_name.upper())
            self.tree.column(column_name, width=width, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_panel = ttk.Frame(self, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Animal", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        r = 0
        self.inputs = {}
        
        fields = [
            ("Nome *", ttk.Entry, {"width": 30}),
            ("Espécie", ttk.Combobox, {"values": ["Gato", "Cachorro", "Pássaro"], "state": "readonly", "width": 30}),
            ("Raça", ttk.Entry, {"width": 30}),
            ("Idade", ttk.Entry, {"width": 30}),
            ("Porte", ttk.Combobox, {"values": SIZES, "state": "readonly", "width": 30}),
            ("Gênero", ttk.Combobox, {"values": GENDERS, "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ["Disponível", "Em processo", "Adotado", "Indisponível"], "state": "readonly", "width": 30}),
            ("Temperamento", ttk.Combobox, {"values": ["Calmo", "Agitado", "Ativo", "Estressado", "Brincalhão", "Dócil"], "state": "readonly", "width": 30}),
            ("Abrigo", ttk.Combobox, {"values": self.get_shelters(), "state": "readonly", "width": 30}),
        ]

        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
            r += 1
            
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Observações"] = tk.Text(self.scrollable_frame, height=4, width=30)
        self.inputs["Observações"].grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
        r += 1

        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()

    def get_shelters(self):
        shelters = session.query(Shelter).all()
        return [f"{s.id} - {s.name}" for s in shelters]

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        animals = session.query(Animal).order_by(Animal.id.desc()).all()
        
        for animal in animals:
            finalized_adoption = any(
                adoption_process.status == "Finalizado" 
                for adoption_process in animal.adoptions
            )
            
            if finalized_adoption:
                animal.status = "Adotado"
                
            shelter_name = animal.shelter.name if animal.shelter else ""
                
            self.tree.insert("", "end", iid=str(animal.id),
                           values=(animal.id, animal.name, animal.species, animal.breed or "", 
                                   animal.age, animal.size or "", animal.gender or "", 
                                   animal.status, shelter_name))
        
        self.inputs["Abrigo"]["values"] = self.get_shelters()
        
        session.commit()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
            
        animal = session.get(Animal, int(sel[0]))
        self.selected_id = animal.id

        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, animal.name or "")
        
        self.inputs["Espécie"].set(animal.species or "")
        
        self.inputs["Raça"].delete(0, tk.END)
        self.inputs["Raça"].insert(0, animal.breed or "")
        
        self.inputs["Idade"].delete(0, tk.END)
        self.inputs["Idade"].insert(0, animal.age or 0)
        
        self.inputs["Porte"].set(animal.size or "")
        self.inputs["Gênero"].set(animal.gender or "")
        self.inputs["Status"].set(animal.status or "")
        self.inputs["Temperamento"].set(animal.temperament or "")
        
        if animal.shelter:
            self.inputs["Abrigo"].set(f"{animal.shelter.id} - {animal.shelter.name}")
        else:
            self.inputs["Abrigo"].set("")
            
        self.inputs["Observações"].delete("1.0", tk.END)
        self.inputs["Observações"].insert(tk.END, animal.health_history or "")

    def new(self):
        self.selected_id = None
        
        for field_name, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)

    def save(self):
        name = self.inputs["Nome *"].get().strip()
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return

        shelter_val = self.inputs["Abrigo"].get().strip()
        
        if shelter_val:
            shelter_id = int(shelter_val.split(" - ")[0])
            shelter = session.get(Shelter, shelter_id)
            
            animais_atuais = session.query(Animal).filter(Animal.shelter_id == shelter_id).count()
            
            if not self.selected_id and animais_atuais >= shelter.capacity:
                messagebox.showerror("Erro", f"Abrigo '{shelter.name}' está lotado (capacidade: {shelter.capacity}).")
                return

        if self.selected_id:
            animal = session.get(Animal, self.selected_id)
        else:
            animal = Animal()
            session.add(animal)

        animal.name = name
        animal.species = self.inputs["Espécie"].get()
        animal.breed = self.inputs["Raça"].get().strip() or None
        
        try: 
            animal.age = int(self.inputs["Idade"].get().strip())
        except: 
            animal.age = 0
            
        animal.size = self.inputs["Porte"].get()
        animal.gender = self.inputs["Gênero"].get()
        animal.status = self.inputs["Status"].get()
        animal.temperament = self.inputs["Temperamento"].get()
        animal.health_history = self.inputs["Observações"].get("1.0", tk.END).strip() or None
        
        if shelter_val:
            animal.shelter_id = shelter_id
        else:
            animal.shelter_id = None

        session.commit()
        self.load()
        messagebox.showinfo("Sucesso", "Animal salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um animal.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir animal selecionado?"):
            return
            
        animal = session.get(Animal, self.selected_id)
        session.delete(animal)
        session.commit()
        
        self.new()
        self.load()
        messagebox.showinfo("Sucesso", "Animal excluído com sucesso.")
