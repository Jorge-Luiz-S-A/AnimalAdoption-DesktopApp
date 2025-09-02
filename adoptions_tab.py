# adoptions_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User
from datetime import datetime

class AdoptionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -------- Left panel: Lista de processos --------
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Processos de Adoção", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame,
                                 columns=("ID","Animal","Usuário","Status","Visita Virtual","Visita Presencial","Data Adoção"),
                                 show="headings", yscrollcommand=scrollbar.set, height=20)
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID",50),("Animal",150),("Usuário",150),("Status",100),
                     ("Visita Virtual",120),("Visita Presencial",120),("Data Adoção",100)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # -------- Right panel: Formulário --------
        right_panel = ttk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Processo", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,10))

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

        # Campos do formulário
        r = 0
        fields = [
            ("Animal *", ttk.Combobox, {"state":"readonly", "width":30}),
            ("Usuário *", ttk.Combobox, {"state":"readonly", "width":30}),
            ("Status", ttk.Combobox, {"values":["","questionnaire","screening","visit","approved","finalized","declined"], "state":"readonly", "width":30}),
            ("Visita Virtual (DD/MM/AAAA)", ttk.Entry, {"width":30}),
            ("Visita Presencial (DD/MM/AAAA)", ttk.Entry, {"width":30}),
            ("Data Adoção (DD/MM/AAAA)", ttk.Entry, {"width":30}),
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5,0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0,5))
            self.inputs[label_text] = w
            r += 1

        # Observações
        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r, column=0, columnspan=2, sticky="w", pady=(5,0)); r+=1
        self.e_notes = tk.Text(self.scrollable_frame, width=30, height=4)
        self.e_notes.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0,5)); r+=1

        # Botões
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()

    # ---------------- Funções ----------------
    def load(self):
        # Atualiza combobox
        self.inputs["Animal *"]['values'] = [f"#{a.id} - {a.name}" for a in session.query(Animal).order_by(Animal.id.desc()).all()]
        self.inputs["Usuário *"]['values'] = [f"#{u.id} - {u.name}" for u in session.query(User).order_by(User.id.desc()).all()]

        # Atualiza lista de processos
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(p.id),
                             values=(p.id,
                                     f"#{p.animal.id} - {p.animal.name}",
                                     f"#{p.user.id} - {p.user.name}",
                                     p.status or "",
                                     p.virtual_visit_at.strftime("%d/%m/%Y") if p.virtual_visit_at else "",
                                     p.in_person_visit_at.strftime("%d/%m/%Y") if p.in_person_visit_at else "",
                                     p.docs_submitted.strftime("%d/%m/%Y") if p.docs_submitted else ""))

    def on_select(self,_):
        sel = self.tree.selection()
        if not sel: return
        p = session.get(AdoptionProcess,int(sel[0]))
        self.selected_id = p.id

        self.inputs["Animal *"].set(f"#{p.animal.id} - {p.animal.name}")
        self.inputs["Usuário *"].set(f"#{p.user.id} - {p.user.name}")
        self.inputs["Status"].set(p.status or "")
        self.inputs["Visita Virtual (DD/MM/AAAA)"].delete(0,tk.END)
        if p.virtual_visit_at:
            self.inputs["Visita Virtual (DD/MM/AAAA)"].insert(0,p.virtual_visit_at.strftime("%d/%m/%Y"))
        self.inputs["Visita Presencial (DD/MM/AAAA)"].delete(0,tk.END)
        if p.in_person_visit_at:
            self.inputs["Visita Presencial (DD/MM/AAAA)"].insert(0,p.in_person_visit_at.strftime("%d/%m/%Y"))
        self.inputs["Data Adoção (DD/MM/AAAA)"].delete(0,tk.END)
        if p.docs_submitted:
            self.inputs["Data Adoção (DD/MM/AAAA)"].insert(0,p.docs_submitted.strftime("%d/%m/%Y"))
        self.e_notes.delete("1.0", tk.END)
        self.e_notes.insert(tk.END, p.notes or "")

    def new(self):
        self.selected_id = None
        for key in self.inputs:
            w = self.inputs[key]
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0,tk.END)
        self.e_notes.delete("1.0",tk.END)

    def save(self):
        if not self.inputs["Animal *"].get() or not self.inputs["Usuário *"].get():
            messagebox.showerror("Erro","Selecione animal e usuário")
            return

        animal_id = int(self.inputs["Animal *"].get().split(" ")[0][1:])
        user_id = int(self.inputs["Usuário *"].get().split(" ")[0][1:])
        a = session.get(Animal, animal_id)
        u = session.get(User, user_id)

        if self.selected_id:
            p = session.get(AdoptionProcess,self.selected_id)
        else:
            p = AdoptionProcess()
            session.add(p)

        p.animal = a
        p.user = u
        p.status = self.inputs["Status"].get()
        p.notes = self.e_notes.get("1.0", tk.END).strip()

        # Função auxiliar para converter string em date
        def parse_date(s):
            s = s.strip()
            if not s:
                return None
            try:
                return datetime.strptime(s, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Erro", f"Data inválida: {s}. Use DD/MM/AAAA")
                raise

        p.virtual_visit_at = parse_date(self.inputs["Visita Virtual (DD/MM/AAAA)"].get())
        p.in_person_visit_at = parse_date(self.inputs["Visita Presencial (DD/MM/AAAA)"].get())
        p.docs_submitted = parse_date(self.inputs["Data Adoção (DD/MM/AAAA)"].get())

        session.commit()
        self.load()
        messagebox.showinfo("Sucesso","Processo salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Erro","Selecione um processo")
            return
        if not messagebox.askyesno("Confirmar","Excluir processo selecionado?"):
            return
        p = session.get(AdoptionProcess,self.selected_id)
        session.delete(p)
        session.commit()
        self.new()
        self.load()
        messagebox.showinfo("Sucesso","Processo excluído com sucesso.")
