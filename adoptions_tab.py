# adoptions_tab.py
import tkinter as tk
from tkinter import ttk
from base_tab import BaseTab
from database import session
from models import AdoptionProcess, Animal, User, Shelter
from utils import ADOPTION_STEPS, parse_int, yes_no
from datetime import datetime

class AdoptionsTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # -------- Left panel: Lista de adoções --------
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Lista de Adoções", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID","Animal","Usuário","Status","Visita Virtual","Visita Presencial","Docs","Check"),
            show="headings", height=20, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID",50),("Animal",140),("Usuário",140),("Status",100),
                     ("Visita Virtual",120),("Visita Presencial",120),("Docs",60),("Check",60)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # -------- Right panel: Formulário --------
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes da Adoção", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,10))

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
            ("Animal *", ttk.Combobox),
            ("Usuário *", ttk.Combobox),
            ("Status", ttk.Combobox, {"values": ADOPTION_STEPS, "state":"readonly"}),
            ("Visita Virtual", ttk.Entry),
            ("Visita Presencial", ttk.Entry),
            ("Docs Enviados", ttk.Combobox, {"values":["","Sim","Não"], "state":"readonly"}),
            ("Check Background", ttk.Combobox, {"values":["","Sim","Não"], "state":"readonly"}),
            ("Notas", ttk.Entry),
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
        btn_frame.grid(row=r,column=0,pady=10)
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()
        self.load_animals()
        self.load_users()

        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas = canvas

    def _on_mousewheel(self, event):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_animals(self):
        animals = session.query(Animal).order_by(Animal.name).all()
        self.inputs["Animal *"]['values'] = [f"{a.name} (ID:{a.id})" for a in animals]

    def load_users(self):
        users = session.query(User).order_by(User.name).all()
        self.inputs["Usuário *"]['values'] = [f"{u.name} (ID:{u.id})" for u in users]

    # ---------------- CRUD ----------------
    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ap in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(ap.id),
                             values=(ap.id,
                                     ap.animal.name if ap.animal else "-",
                                     ap.user.name if ap.user else "-",
                                     ap.status or "-",
                                     ap.virtual_visit_at.strftime("%d/%m/%Y") if ap.virtual_visit_at else "-",
                                     ap.in_person_visit_at.strftime("%d/%m/%Y") if ap.in_person_visit_at else "-",
                                     yes_no(ap.docs_submitted),
                                     yes_no(ap.background_check_ok)))

    def on_select(self,_):
        sel = self.tree.selection()
        if not sel: return
        ap = session.get(AdoptionProcess,int(sel[0]))
        self.selected_id = ap.id

        self.inputs["Animal *"].set(f"{ap.animal.name} (ID:{ap.animal.id})" if ap.animal else "")
        self.inputs["Usuário *"].set(f"{ap.user.name} (ID:{ap.user.id})" if ap.user else "")
        self.inputs["Status"].set(ap.status or "")
        self.inputs["Visita Virtual"].delete(0, tk.END)
        self.inputs["Visita Virtual"].insert(0, ap.virtual_visit_at.strftime("%d/%m/%Y") if ap.virtual_visit_at else "")
        self.inputs["Visita Presencial"].delete(0, tk.END)
        self.inputs["Visita Presencial"].insert(0, ap.in_person_visit_at.strftime("%d/%m/%Y") if ap.in_person_visit_at else "")
        self.inputs["Docs Enviados"].set(yes_no(ap.docs_submitted))
        self.inputs["Check Background"].set(yes_no(ap.background_check_ok))
        self.inputs["Notas"].delete(0, tk.END)
        self.inputs["Notas"].insert(0, ap.notes or "")

    def new(self):
        self.selected_id = None
        for key, w in self.inputs.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, tk.END)

    def save(self):
        # Validação obrigatória
        animal_val = self.inputs["Animal *"].get()
        user_val = self.inputs["Usuário *"].get()
        if not animal_val or not user_val:
            self.error("Animal e Usuário são obrigatórios.")
            return

        # Obter animal e usuário
        animal_id = int(animal_val.split("ID:")[1].strip(")"))
        user_id = int(user_val.split("ID:")[1].strip(")"))
        animal = session.get(Animal, animal_id)
        user = session.get(User, user_id)

        if self.selected_id:
            ap = session.get(AdoptionProcess, self.selected_id)
            prev_status = ap.status
        else:
            ap = AdoptionProcess()
            session.add(ap)
            prev_status = None

        ap.animal = animal
        ap.user = user
        ap.status = self.inputs["Status"].get() or None

        # Conversão de datas para datetime
        virtual_str = self.inputs["Visita Virtual"].get().strip()
        in_person_str = self.inputs["Visita Presencial"].get().strip()
        ap.virtual_visit_at = datetime.strptime(virtual_str, "%d/%m/%Y") if virtual_str else None
        ap.in_person_visit_at = datetime.strptime(in_person_str, "%d/%m/%Y") if in_person_str else None

        ap.docs_submitted = self.inputs["Docs Enviados"].get() == "Sim"
        ap.background_check_ok = self.inputs["Check Background"].get() == "Sim"
        ap.notes = self.inputs["Notas"].get().strip() or None

        # Atualiza adotados automaticamente se status finalizado
        if ap.status == "Finalizado" and (prev_status != "Finalizado"):
            shelter = session.query(Shelter).filter_by(name=animal.location).first()
            if shelter:
                shelter.adopted_count = (shelter.adopted_count or 0) + 1

        session.commit()
        self.load()
        self.load_animals()
        self.load_users()
        self.info("Processo de adoção salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            self.error("Selecione um processo de adoção.")
            return
        ap = session.get(AdoptionProcess,self.selected_id)
        session.delete(ap)
        session.commit()
        self.new()
        self.load()
        self.info("Processo de adoção excluído com sucesso.")
