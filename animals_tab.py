# animals_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import json

from base_tab import BaseTab
from database import session
from models import Animal
from utils import STATUSES, SIZES, GENDERS, parse_int, combobox_set

class AnimalsTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Table
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="Lista de Animais", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Table with scrollbar
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(table_frame, columns=("id","name","species","age","size","gender","status","location"), 
                                show="headings", height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        for c, w in (("id",60), ("name",140), ("species",100), ("age",60), ("size",80), ("gender",80), ("status",100), ("location",120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right panel - Form
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        ttk.Label(right_panel, text="Detalhes do Animal", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Form container with scrollbar
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(form_container, height=500)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        r = 0
        r = self.create_form_field(scrollable_frame, "Nome *", r, True)
        self.e_name = ttk.Entry(scrollable_frame, width=32); self.e_name.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Espécie *", r, True)
        self.e_species = ttk.Entry(scrollable_frame); self.e_species.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Raça", r)
        self.e_breed = ttk.Entry(scrollable_frame); self.e_breed.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Idade (anos)", r)
        self.e_age = ttk.Entry(scrollable_frame); self.e_age.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Porte", r)
        self.cb_size = ttk.Combobox(scrollable_frame, values=SIZES, state="readonly"); self.cb_size.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Gênero", r)
        self.cb_gender = ttk.Combobox(scrollable_frame, values=GENDERS, state="readonly"); self.cb_gender.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Vacinado", r)
        self.cb_vacc = ttk.Combobox(scrollable_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_vacc.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Castrado", r)
        self.cb_neut = ttk.Combobox(scrollable_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_neut.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Temperamento", r)
        self.e_temp = ttk.Entry(scrollable_frame); self.e_temp.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Histórico de Saúde", r)
        self.e_health = ttk.Entry(scrollable_frame); self.e_health.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Status", r)
        self.cb_status = ttk.Combobox(scrollable_frame, values=STATUSES, state="readonly"); self.cb_status.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Local", r)
        self.e_location = ttk.Entry(scrollable_frame); self.e_location.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Fotos (JSON array)", r, False, "Ex: [\"url1\", \"url2\"]")
        self.e_photos = ttk.Entry(scrollable_frame); self.e_photos.grid(row=r, column=0, sticky="we", pady=(0, 15)); r+=1

        # Buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=r, column=0, sticky="we", pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save, style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        # Configure grid
        scrollable_frame.columnconfigure(0, weight=1)
        self.selected_id = None
        self.load()

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for a in session.query(Animal).order_by(Animal.id.desc()).all():
            self.tree.insert("", "end", iid=str(a.id),
                             values=(a.id, a.name, a.species, a.age, a.size or "", a.gender or "", a.status, a.location or ""))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        a = session.get(Animal, int(sel[0]))
        self.selected_id = a.id
        self.e_name.delete(0, tk.END); self.e_name.insert(0, a.name or "")
        self.e_species.delete(0, tk.END); self.e_species.insert(0, a.species or "")
        self.e_breed.delete(0, tk.END); self.e_breed.insert(0, a.breed or "")
        self.e_age.delete(0, tk.END); self.e_age.insert(0, str(a.age or 0))
        combobox_set(self.cb_size, a.size or "")
        combobox_set(self.cb_gender, a.gender or "")
        self.cb_vacc.set("Sim" if a.vaccinated else ("Não" if a.vaccinated is False else ""))
        self.cb_neut.set("Sim" if a.neutered else ("Não" if a.neutered is False else ""))
        self.e_temp.delete(0, tk.END); self.e_temp.insert(0, a.temperament or "")
        self.e_health.delete(0, tk.END); self.e_health.insert(0, a.health_history or "")
        combobox_set(self.cb_status, a.status or "available")
        self.e_location.delete(0, tk.END); self.e_location.insert(0, a.location or "")
        self.e_photos.delete(0, tk.END); self.e_photos.insert(0, a.photo_urls_json or "[]")

    def new(self):
        self.selected_id = None
        for e in (self.e_name, self.e_species, self.e_breed, self.e_age, self.e_temp, self.e_health, self.e_location, self.e_photos):
            e.delete(0, tk.END)
        self.cb_size.set(""); self.cb_gender.set(""); self.cb_vacc.set(""); self.cb_neut.set(""); self.cb_status.set("available")

    def save(self):
        name = self.e_name.get().strip()
        species = self.e_species.get().strip()
        if not name or not species:
            self.error("Nome e Espécie são obrigatórios.")
            return
        age = parse_int(self.e_age.get() or "0", 0)
        try:
            photos_json = self.e_photos.get().strip() or "[]"
            json.loads(photos_json)
        except Exception:
            self.error("Fotos deve ser uma lista JSON (ex: [\"http://...\"])")
            return

        if self.selected_id:
            a = session.get(Animal, self.selected_id)
        else:
            a = Animal()
            session.add(a)

        a.name = name
        a.species = species
        a.breed = self.e_breed.get().strip() or None
        a.age = age
        a.size = self.cb_size.get() or None
        a.gender = self.cb_gender.get() or None
        a.vaccinated = (self.cb_vacc.get() == "Sim")
        a.neutered = (self.cb_neut.get() == "Sim")
        a.temperament = self.e_temp.get().strip() or None
        a.health_history = self.e_health.get().strip() or None
        a.status = self.cb_status.get() or "available"
        a.location = self.e_location.get().strip() or None
        a.photo_urls_json = photos_json

        session.commit()
        self.load()
        self.info("Animal salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            self.error("Selecione um registro.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir animal selecionado?"):
            return
        a = session.get(Animal, self.selected_id)
        session.delete(a)
        session.commit()
        self.new()
        self.load()
        self.info("Animal excluído com sucesso.")
