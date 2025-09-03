# shelter_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Shelter, Animal, AdoptionProcess

class ShelterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -------- Left panel: Lista de abrigos --------
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Lista de Abrigos", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID","Nome","Email","Telefone","Endereço","Autenticidade","Resgatados","Adotados"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        for c,w in (("ID",40),("Nome",150),("Email",180),("Telefone",100),("Endereço",150),
                    ("Autenticidade",80),("Resgatados",80),("Adotados",80)):
            self.tree.heading(c,text=c.upper())
            self.tree.column(c,width=w,anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # -------- Right panel: Formulário --------
        right_panel = ttk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Abrigo", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,10))

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

        # Campos do formulário (Label acima do input) — sem Resgatados e Adotados
        r = 0
        fields = [
            ("Nome", ttk.Entry, {"width":30}),
            ("Email", ttk.Entry, {"width":30}),
            ("Telefone", ttk.Entry, {"width":30}),
            ("Endereço", ttk.Entry, {"width":30}),
            ("Autenticidade", ttk.Combobox, {"values":["","Sim","Não"], "state":"readonly", "width":30}),
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r,column=0,columnspan=2,sticky="w", pady=(5,0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r,column=0,columnspan=2,sticky="we", pady=(0,5))
            self.inputs[label_text] = w
            r += 1

        # Botões
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r,column=0,columnspan=2,pady=10)
        ttk.Button(btn_frame,text="Novo",command=self.new).pack(side=tk.LEFT,padx=4)
        ttk.Button(btn_frame,text="Salvar",command=self.save).pack(side=tk.LEFT,padx=4)
        ttk.Button(btn_frame,text="Excluir",command=self.delete).pack(side=tk.LEFT,padx=4)
        ttk.Button(btn_frame,text="Atualizar",command=self.load).pack(side=tk.LEFT,padx=4)

        self.selected_id = None
        self.load()

    # ---------------- Funções ----------------
    def load(self):
        # Limpa tabela
        for i in self.tree.get_children():
            self.tree.delete(i)

        shelters = session.query(Shelter).order_by(Shelter.id.desc()).all()
        for s in shelters:
            # Contar animais resgatados no abrigo
            rescued_count = session.query(Animal).filter(Animal.location==s.name).count()
            # Contar animais adotados do abrigo
            adopted_count = (
                session.query(Animal)
                .join(Animal.adoptions)
                .filter(Animal.location==s.name, AdoptionProcess.status=="Finalizado")
                .count()
            )

            self.tree.insert(
                "",
                "end",
                iid=str(s.id),
                values=(
                    s.id,
                    s.name or "",
                    s.email or "",
                    s.phone or "",
                    s.address or "",
                    "Sim" if s.authenticity_verified else "Não",
                    rescued_count,
                    adopted_count
                )
            )

    def on_select(self,_):
        sel = self.tree.selection()
        if not sel: return
        s = session.get(Shelter,int(sel[0]))
        self.selected_id = s.id

        self.inputs["Nome"].delete(0,tk.END); self.inputs["Nome"].insert(0,s.name or "")
        self.inputs["Email"].delete(0,tk.END); self.inputs["Email"].insert(0,s.email or "")
        self.inputs["Telefone"].delete(0,tk.END); self.inputs["Telefone"].insert(0,s.phone or "")
        self.inputs["Endereço"].delete(0,tk.END); self.inputs["Endereço"].insert(0,s.address or "")
        self.inputs["Autenticidade"].set("Sim" if s.authenticity_verified else "Não")

    def new(self):
        self.selected_id = None
        for key, w in self.inputs.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0,tk.END)

    def save(self):
        if self.selected_id:
            s = session.get(Shelter,self.selected_id)
        else:
            s = Shelter()
            session.add(s)

        s.name = self.inputs["Nome"].get().strip() or "Meu Abrigo"
        s.email = self.inputs["Email"].get().strip() or None
        s.phone = self.inputs["Telefone"].get().strip() or None
        s.address = self.inputs["Endereço"].get().strip() or None
        s.authenticity_verified = (self.inputs["Autenticidade"].get()=="Sim")

        session.commit()
        self.load()
        messagebox.showinfo("Sucesso","Abrigo salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Erro","Selecione um abrigo.")
            return
        if not messagebox.askyesno("Confirmar","Excluir abrigo selecionado?"):
            return
        s = session.get(Shelter,self.selected_id)
        session.delete(s)
        session.commit()
        self.new()
        self.load()
        messagebox.showinfo("Sucesso","Abrigo excluído com sucesso.")
