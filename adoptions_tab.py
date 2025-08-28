# adoptions_tab.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from base_tab import BaseTab
from database import session
from models import AdoptionProcess, Animal, User, Shelter
from utils import ADOPTION_STEPS, parse_int, parse_dt_str, yes_no, combobox_set

class AdoptionsTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Table
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="Processos de Adoção", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Table with scrollbar
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame, columns=("ID","Animal","Usuário","Status","Score","Visita Virtual","Visita Pres.","Docs","BG Check"), 
                                show="headings", height=12, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        heads = ("ID","Animal","Usuário","Status","Score","Visita Virtual","Visita Pres.","Docs","BG Check")
        for c, h, w in zip(self.tree["columns"], heads, (60,160,160,110,70,140,120,70,80)):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right panel - Form
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        ttk.Label(right_panel, text="Detalhes do Processo", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Form container with scrollbar
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(form_container, height=500)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        r = 0
        r = self.create_form_field(scrollable_frame, "Animal *", r, True)
        self.cb_animal = ttk.Combobox(scrollable_frame, state="readonly", width=40); self.cb_animal.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Usuário *", r, True)
        self.cb_user = ttk.Combobox(scrollable_frame, state="readonly", width=40); self.cb_user.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Status", r)
        self.cb_status = ttk.Combobox(scrollable_frame, values=ADOPTION_STEPS, state="readonly"); self.cb_status.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Score (0-100)", r)
        self.e_score = ttk.Entry(scrollable_frame); self.e_score.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Visita Virtual", r, False, "YYYY-MM-DD HH:MM")
        self.e_vvisit = ttk.Entry(scrollable_frame); self.e_vvisit.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Visita Presencial", r, False, "YYYY-MM-DD HH:MM")
        self.e_pvisit = ttk.Entry(scrollable_frame); self.e_pvisit.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Docs enviados", r)
        self.cb_docs = ttk.Combobox(scrollable_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_docs.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "BG Check OK", r)
        self.cb_bg = ttk.Combobox(scrollable_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_bg.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Notas", r)
        self.e_notes = ttk.Entry(scrollable_frame); self.e_notes.grid(row=r, column=0, sticky="we", pady=(0, 15)); r+=1

        # Buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=r, column=0, sticky="we", pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save, style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        scrollable_frame.columnconfigure(0, weight=1)
        self.selected_id = None
        self.reload_refs()
        self.load()

    def reload_refs(self):
        self._animals = session.query(Animal).order_by(Animal.name).all()
        self._users = session.query(User).order_by(User.name).all()
        self.cb_animal["values"] = [f"#{a.id} - {a.name} ({a.species})" for a in self._animals]
        self.cb_user["values"] = [f"#{u.id} - {u.name} <{u.email}>" for u in self._users]

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ad in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(ad.id),
                values=(
                    ad.id,
                    f"#{ad.animal_id} - {ad.animal.name if ad.animal else ''}",
                    f"#{ad.user_id} - {ad.user.name if ad.user else ''}",
                    ad.status,
                    ad.questionnaire_score if ad.questionnaire_score is not None else "",
                    ad.virtual_visit_at.strftime("%Y-%m-%d %H:%M") if ad.virtual_visit_at else "",
                    ad.in_person_visit_at.strftime("%Y-%m-%d %H:%M") if ad.in_person_visit_at else "",
                    yes_no(ad.docs_submitted),
                    yes_no(ad.background_check_ok),
                )
            )

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        ad = session.get(AdoptionProcess, int(sel[0]))
        self.selected_id = ad.id
        self.reload_refs()
        ai = next((i for i, a in enumerate(self._animals) if a.id == ad.animal_id), -1)
        ui = next((i for i, u in enumerate(self._users) if u.id == ad.user_id), -1)
        if ai >= 0: self.cb_animal.current(ai)
        if ui >= 0: self.cb_user.current(ui)
        self.cb_status.set(ad.status or "questionnaire")
        self.e_score.delete(0, tk.END); self.e_score.insert(0, "" if ad.questionnaire_score is None else str(ad.questionnaire_score))
        self.e_vvisit.delete(0, tk.END); self.e_vvisit.insert(0, ad.virtual_visit_at.strftime("%Y-%m-%d %H:%M") if ad.virtual_visit_at else "")
        self.e_pvisit.delete(0, tk.END); self.e_pvisit.insert(0, ad.in_person_visit_at.strftime("%Y-%m-%d %H:%M") if ad.in_person_visit_at else "")
        self.cb_docs.set("Sim" if ad.docs_submitted else "Não")
        if ad.background_check_ok is None:
            self.cb_bg.set("")
        else:
            self.cb_bg.set("Sim" if ad.background_check_ok else "Não")
        self.e_notes.delete(0, tk.END); self.e_notes.insert(0, ad.notes or "")

    def new(self):
        self.selected_id = None
        self.reload_refs()
        self.cb_animal.set(""); self.cb_user.set("")
        self.cb_status.set("questionnaire")
        for e in (self.e_score, self.e_vvisit, self.e_pvisit, self.e_notes):
            e.delete(0, tk.END)
        self.cb_docs.set(""); self.cb_bg.set("")

    def save(self):
        if self.cb_animal.current() < 0 or self.cb_user.current() < 0:
            self.error("Selecione Animal e Usuário.")
            return
        animal = self._animals[self.cb_animal.current()]
        user = self._users[self.cb_user.current()]

        if self.selected_id:
            ad = session.get(AdoptionProcess, self.selected_id)
        else:
            ad = AdoptionProcess()
            session.add(ad)

        ad.animal_id = animal.id
        ad.user_id = user.id
        ad.status = self.cb_status.get() or "questionnaire"
        ad.questionnaire_score = parse_int(self.e_score.get() or "0", 0) if self.e_score.get().strip() else None
        ad.virtual_visit_at = parse_dt_str(self.e_vvisit.get().strip())
        ad.in_person_visit_at = parse_dt_str(self.e_pvisit.get().strip())
        ad.docs_submitted = (self.cb_docs.get() == "Sim")
        bg = self.cb_bg.get()
        ad.background_check_ok = True if bg == "Sim" else False if bg == "Não" else None
        ad.notes = self.e_notes.get().strip() or None

        # Regras simples para atualizar status do animal / métricas abrigo
        animal_obj = session.get(Animal, ad.animal_id)
        if ad.status in ("screening", "visit", "docs", "approved"):
            animal_obj.status = "in_process"
        elif ad.status == "finalized":
            animal_obj.status = "adopted"
            s = session.query(Shelter).first()
            if s:
                s.adopted_count = (s.adopted_count or 0) + 1

        session.commit()
        self.load()
        self.info("Processo de adoção salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            self.error("Selecione um registro.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir processo de adoção selecionado?"):
            return
        ad = session.get(AdoptionProcess, self.selected_id)
        session.delete(ad)
        session.commit()
        self.new()
        self.load()
        self.info("Processo de adoção excluído com sucesso.")
