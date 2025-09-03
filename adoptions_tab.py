"""
Aba de Adoções
--------------
Gerencia todos os processos de adoção com formulário completo.
Inclui campos para datas de visita online e presencial.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User
from utils import ADOPTION_STEPS

class AdoptionsTab(ttk.Frame):
    """
    Aba para gerenciamento de processos de adoção.
    
    Funcionalidades:
    - Listar todos os processos de adoção
    - Criar, editar e excluir processos
    - Registrar datas de visitas online e presencial
    - Vincular animais e usuários aos processos
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de adoções.
        
        Args:
            parent: Widget pai onde a aba será inserida
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -------- LEFT: Lista de adoções --------
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

        # -------- RIGHT: Formulário --------
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes da Adoção", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Scrollable form
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

        # Campos do formulário
        r = 0
        fields = [
            ("Animal *", ttk.Combobox, {"values": self.get_animals(), "state": "readonly", "width": 30}),
            ("Usuário *", ttk.Combobox, {"values": self.get_users(), "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ADOPTION_STEPS, "state": "readonly", "width": 30}),
            ("Visita Online", ttk.Entry, {"width": 30}),  # NOVO CAMPO
            ("Visita Presencial", ttk.Entry, {"width": 30}),  # NOVO CAMPO
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        # Campo Notas
        ttk.Label(self.scrollable_frame, text="Notas").grid(row=r, column=0, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Notas"] = tk.Text(self.scrollable_frame, width=30, height=5, wrap="word")
        self.inputs["Notas"].grid(row=r, column=0, sticky="we", pady=(0, 5))
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

    # ---------------- Funções Auxiliares ----------------
    def get_animals(self):
        """
        Obtém a lista de animais para popular o combobox.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para todos os animais
        """
        return [f"{a.id} - {a.name}" for a in session.query(Animal).all()]

    def get_users(self):
        """
        Obtém a lista de usuários para popular o combobox.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para todos os usuários
        """
        return [f"{u.id} - {u.name}" for u in session.query(User).all()]

    # ---------------- CRUD ----------------
    def load(self):
        """
        Carrega todas as adoções na Treeview.
        
        Atualiza as listas de animais e usuários nos comboboxes.
        """
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ad in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(ad.id),
                             values=(ad.id,
                                     ad.animal.name if ad.animal else "-",
                                     ad.user.name if ad.user else "-",
                                     ad.status or "-"))

        # Atualizar listas de combobox
        self.inputs["Animal *"]["values"] = self.get_animals()
        self.inputs["Usuário *"]["values"] = self.get_users()

    def on_select(self, event):
        """
        Manipula a seleção de uma adoção na lista.
        
        Args:
            event: Evento de seleção da Treeview
        """
        sel = self.tree.selection()
        if not sel:
            return
        ad = session.get(AdoptionProcess, int(sel[0]))
        self.selected_id = ad.id

        self.inputs["Animal *"].set(f"{ad.animal.id} - {ad.animal.name}" if ad.animal else "")
        self.inputs["Usuário *"].set(f"{ad.user.id} - {ad.user.name}" if ad.user else "")
        self.inputs["Status"].set(ad.status or "")
        
        # NOVOS CAMPOS - Datas de visita
        self.inputs["Visita Online"].delete(0, tk.END)
        if ad.virtual_visit_at:
            self.inputs["Visita Online"].insert(0, ad.virtual_visit_at.strftime("%d/%m/%Y"))
            
        self.inputs["Visita Presencial"].delete(0, tk.END)
        if ad.in_person_visit_at:
            self.inputs["Visita Presencial"].insert(0, ad.in_person_visit_at.strftime("%d/%m/%Y"))
            
        self.inputs["Notas"].delete("1.0", tk.END)
        self.inputs["Notas"].insert("1.0", ad.notes or "")

    def new(self):
        """Limpa o formulário para criar uma nova adoção."""
        self.selected_id = None
        for key, w in self.inputs.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            elif isinstance(w, tk.Text):
                w.delete("1.0", tk.END)
            elif isinstance(w, tk.Entry):
                w.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um processo de adoção.
        
        Valida o formato das datas de visita antes de salvar.
        """
        animal_val = self.inputs["Animal *"].get().strip()
        user_val = self.inputs["Usuário *"].get().strip()

        if not animal_val or not user_val:
            messagebox.showerror("Erro", "Animal e Usuário são obrigatórios.")
            return

        animal_id = int(animal_val.split(" - ")[0])
        user_id = int(user_val.split(" - ")[0])

        if self.selected_id:
            ad = session.get(AdoptionProcess, self.selected_id)
        else:
            ad = AdoptionProcess()
            session.add(ad)

        ad.animal_id = animal_id
        ad.user_id = user_id
        ad.status = self.inputs["Status"].get().strip() or None
        ad.notes = self.inputs["Notas"].get("1.0", tk.END).strip() or None
        
        # NOVOS CAMPOS - Datas de visita (com validação)
        from datetime import datetime
        
        visita_online = self.inputs["Visita Online"].get().strip()
        visita_presencial = self.inputs["Visita Presencial"].get().strip()
        
        try:
            if visita_online:
                ad.virtual_visit_at = datetime.strptime(visita_online, "%d/%m/%Y")
            else:
                ad.virtual_visit_at = None
                
            if visita_presencial:
                ad.in_person_visit_at = datetime.strptime(visita_presencial, "%d/%m/%Y")
            else:
                ad.in_person_visit_at = None
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        # Salvar adoção primeiro
        session.commit()
        
        # ATUALIZAR STATUS DO ANIMAL AUTOMATICAMENTE
        ad.update_animal_status()
        
        session.commit()
        self.load()
        messagebox.showinfo("Sucesso", "Adoção salva com sucesso.")

    def delete(self):
        """Exclui o processo de adoção selecionado após confirmação."""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione uma adoção.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir adoção selecionada?"):
            return
        ad = session.get(AdoptionProcess, self.selected_id)
        
        # Restaurar status do animal para "Disponível" antes de excluir
        if ad.animal:
            ad.animal.status = "Disponível"
        
        session.delete(ad)
        session.commit()
        self.new()
        self.load()
        messagebox.showinfo("Sucesso", "Adoção excluída com sucesso.")
