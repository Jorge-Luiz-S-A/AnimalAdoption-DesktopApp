import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User
from utils import ADOPTION_STEPS

class AdoptionsTab(ttk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(left_panel, text="Lista de Adoções", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Animal", "Usuário", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID", 50), ("Animal", 150), ("Usuário", 150), ("Status", 120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes da Adoção", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

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
        fields = [
            ("Animal *", ttk.Combobox, {"values": self.get_animals(), "state": "readonly", "width": 30}),
            ("Usuário *", ttk.Combobox, {"values": self.get_users(), "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ADOPTION_STEPS, "state": "readonly", "width": 30}),
            ("Visita Online", ttk.Entry, {"width": 30}),
            ("Visita Presencial", ttk.Entry, {"width": 30}),
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        ttk.Label(self.scrollable_frame, text="Notas").grid(row=r, column=0, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Notas"] = tk.Text(self.scrollable_frame, width=30, height=5, wrap="word")
        self.inputs["Notas"].grid(row=r, column=0, sticky="we", pady=(0, 5))
        r += 1

        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        self.selected_id = None
        self.load()

    def get_animals(self):
        animais_disponiveis = session.query(Animal).filter(
            Animal.status == "Disponível"
        ).all()
        
        return [f"{a.id} - {a.name}" for a in animais_disponiveis]
    
    def get_users(self):
        usuarios_aprovados = session.query(User).filter(
            User.approved == True
        ).all()
        
        return [f"{u.id} - {u.name}" for u in usuarios_aprovados]

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for adocao in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(adocao.id),
                           values=(adocao.id,
                                   adocao.animal.name if adocao.animal else "-",
                                   adocao.user.name if adocao.user else "-",
                                   adocao.status or "-"))

        self.inputs["Animal *"]["values"] = self.get_animals()
        self.inputs["Usuário *"]["values"] = self.get_users()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
            
        adocao = session.get(AdoptionProcess, int(sel[0]))
        self.selected_id = adocao.id

        if adocao.animal:
            self.inputs["Animal *"].set(f"{adocao.animal.id} - {adocao.animal.name}")
        else:
            self.inputs["Animal *"].set("")
            
        if adocao.user:
            self.inputs["Usuário *"].set(f"{adocao.user.id} - {adocao.user.name}")
        else:
            self.inputs["Usuário *"].set("")
            
        self.inputs["Status"].set(adocao.status or "")
        
        self.inputs["Visita Online"].delete(0, tk.END)
        if adocao.virtual_visit_at:
            self.inputs["Visita Online"].insert(0, adocao.virtual_visit_at.strftime("%d/%m/%Y"))
            
        self.inputs["Visita Presencial"].delete(0, tk.END)
        if adocao.in_person_visit_at:
            self.inputs["Visita Presencial"].insert(0, adocao.in_person_visit_at.strftime("%d/%m/%Y"))
            
        self.inputs["Notas"].delete("1.0", tk.END)
        self.inputs["Notas"].insert("1.0", adocao.notes or "")

    def new(self):
        self.selected_id = None
        for key, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def save(self):
        animal_val = self.inputs["Animal *"].get().strip()
        user_val = self.inputs["Usuário *"].get().strip()

        if not animal_val or not user_val:
            messagebox.showerror("Erro", "Animal e Usuário são obrigatórios.")
            return

        animal_id = int(animal_val.split(" - ")[0])
        user_id = int(user_val.split(" - ")[0])

        if self.selected_id:
            adocao = session.get(AdoptionProcess, self.selected_id)
        else:
            adocao = AdoptionProcess()
            session.add(adocao)

        adocao.animal_id = animal_id
        adocao.user_id = user_id
        adocao.status = self.inputs["Status"].get().strip() or None
        adocao.notes = self.inputs["Notas"].get("1.0", tk.END).strip() or None

        from datetime import datetime
        visita_online = self.inputs["Visita Online"].get().strip()
        visita_presencial = self.inputs["Visita Presencial"].get().strip()
        
        try:
            if visita_online:
                adocao.virtual_visit_at = datetime.strptime(visita_online, "%d/%m/%Y")
            else:
                adocao.virtual_visit_at = None
                
            if visita_presencial:
                adocao.in_person_visit_at = datetime.strptime(visita_presencial, "%d/%m/%Y")
            else:
                adocao.in_person_visit_at = None
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        try:
            session.commit()
            
            self.atualizar_status_animal(adocao)
            session.commit()
            
            self.load()
            messagebox.showinfo("Sucesso", "Adoção salva com sucesso. Status do animal atualizado automaticamente.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar adoção: {e}")

    def atualizar_status_animal(self, adopcao):
        if adopcao.animal:
            if adopcao.status == "Finalizado":
                adopcao.animal.status = "Adotado"
            elif adopcao.status in ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado"]:
                adopcao.animal.status = "Em processo"

    def delete(self):
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione uma adoção.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir adoção selecionada?"):
            return
            
        try:
            adocao = session.get(AdoptionProcess, self.selected_id)
            
            if adocao.animal:
                adocao.animal.status = "Disponível"
            
            session.delete(adocao)
            session.commit()
            
            self.new()
            self.load()
            messagebox.showinfo("Sucesso", "Adoção excluída com sucesso. Status do animal restaurado para Disponível.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir adoção: {e}")
