import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from base_tab import BaseTab
from database import session
from models import Animal, Shelter
from utils import SIZES, GENDERS, parse_int, combobox_set

class AnimalsTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # -------- Left panel: Lista de animais --------
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Lista de Animais", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID","Nome","Espécie","Idade","Porte","Sexo","Status","Local"),
            show="headings", height=20, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID",60), ("Nome",140), ("Espécie",100), ("Idade",60), ("Porte",80),
                     ("Sexo",80), ("Status",100), ("Local",120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # -------- Right panel: Formulário --------
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Animal", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,10))

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
            ("Nome *", ttk.Entry),
            ("Espécie *", ttk.Entry),
            ("Raça", ttk.Entry),
            ("Idade", ttk.Entry),
            ("Porte", ttk.Combobox, {"values": SIZES, "state": "readonly"}),
            ("Sexo", ttk.Combobox, {"values": GENDERS, "state": "readonly"}),
            ("Vacinado", ttk.Combobox, {"values": ["","Sim","Não"], "state": "readonly"}),
            ("Castrado", ttk.Combobox, {"values": ["","Sim","Não"], "state": "readonly"}),
            ("Temperamento", ttk.Entry),
            ("Histórico de saúde", ttk.Entry),
            ("Status", ttk.Combobox, {"values":["","Disponível","Em processo","Adotado","Indisponível"], "state":"readonly"}),
            ("Abrigo", ttk.Combobox, {"state":"readonly"}),  # substitui Local
        ]

        self.inputs = {}
        for label_text, widget_class, *opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r,column=0,sticky="w", pady=(5,0))
            r += 1
            w_opts = opts[0] if opts else {}
            w = widget_class(self.scrollable_frame, **w_opts)
            w.grid(row=r, column=0, sticky="we", pady=(0,10))
            self.inputs[label_text] = w
            r += 1

        # Botões
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, pady=10)
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()
        self.load_shelters()

        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas = canvas

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_shelters(self):
        shelters = session.query(Shelter).order_by(Shelter.name).all()
        self.inputs["Abrigo"]['values'] = [s.name for s in shelters]

    # ---------------- CRUD ----------------
    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for a in session.query(Animal).order_by(Animal.id.desc()).all():
            self.tree.insert("", "end", iid=str(a.id),
                             values=(a.id, a.name, a.species, a.age, a.size or "", a.gender or "",
                                     a.status or "", a.location or ""))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        a = session.get(Animal, int(sel[0]))
        self.selected_id = a.id

        self.inputs["Nome *"].delete(0, tk.END); self.inputs["Nome *"].insert(0, a.name or "")
        self.inputs["Espécie *"].delete(0, tk.END); self.inputs["Espécie *"].insert(0, a.species or "")
        self.inputs["Raça"].delete(0, tk.END); self.inputs["Raça"].insert(0, a.breed or "")
        self.inputs["Idade"].delete(0, tk.END); self.inputs["Idade"].insert(0, str(a.age or 0))
        self.inputs["Porte"].set(a.size or "")
        self.inputs["Sexo"].set(a.gender or "")
        self.inputs["Vacinado"].set("Sim" if a.vaccinated else "Não")
        self.inputs["Castrado"].set("Sim" if a.neutered else "Não")
        self.inputs["Temperamento"].delete(0, tk.END); self.inputs["Temperamento"].insert(0, a.temperament or "")
        self.inputs["Histórico de saúde"].delete(0, tk.END); self.inputs["Histórico de saúde"].insert(0, a.health_history or "")
        self.inputs["Status"].set(a.status or "")
        self.inputs["Abrigo"].set(a.location or "")

    def new(self):
        self.selected_id = None
        for key, w in self.inputs.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, tk.END)

    def save(self):
        if not self.inputs["Nome *"].get().strip() or not self.inputs["Espécie *"].get().strip():
            self.error("Nome e Espécie são obrigatórios.")
            return
        if self.selected_id:
            a = session.get(Animal, self.selected_id)
        else:
            a = Animal()
            session.add(a)

        a.name = self.inputs["Nome *"].get().strip()
        a.species = self.inputs["Espécie *"].get().strip()
        a.breed = self.inputs["Raça"].get().strip() or None
        a.age = parse_int(self.inputs["Idade"].get() or "0", 0)
        a.size = self.inputs["Porte"].get() or None
        a.gender = self.inputs["Sexo"].get() or None
        a.vaccinated = self.inputs["Vacinado"].get() == "Sim"
        a.neutered = self.inputs["Castrado"].get() == "Sim"
        a.temperament = self.inputs["Temperamento"].get().strip() or None
        a.health_history = self.inputs["Histórico de saúde"].get().strip() or None
        a.status = self.inputs["Status"].get() or None

        shelter_name = self.inputs["Abrigo"].get()
        if shelter_name:
            shelter = session.query(Shelter).filter_by(name=shelter_name).first()
            if shelter:
                a.location = shelter.name
                # Incrementa resgatados se for novo animal
                if not self.selected_id:
                    shelter.rescued_count = (shelter.rescued_count or 0) + 1

        session.commit()
        self.load()
        self.load_shelters()
        self.info("Animal salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            self.error("Selecione um registro.")
            return
        a = session.get(Animal, self.selected_id)
        session.delete(a)
        session.commit()
        self.new()
        self.load()
        self.info("Animal excluído com sucesso.")
