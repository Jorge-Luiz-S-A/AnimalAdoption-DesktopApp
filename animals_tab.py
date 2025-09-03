"""
Aba de Animais - CRUD completo
------------------------------
Permite gerenciar todos os animais do sistema com formulário scrollável e edição de registros existentes.
Inclui vínculo com abrigos e validação de capacidade.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal, AdoptionProcess
from utils import SIZES, GENDERS

class AnimalsTab(ttk.Frame):
    """
    Aba para gerenciamento de animais.
    
    Funcionalidades:
    - Listar todos os animais
    - Criar, editar e excluir animais
    - Vincular animais a abrigos
    - Validar capacidade dos abrigos
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de animais.
        
        Args:
            parent: Widget pai onde a aba será inserida
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Lista de animais
        left_panel = ttk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        ttk.Label(left_panel, text="Lista de Animais", font=("Arial",10,"bold")).pack(anchor=tk.W, pady=(0,5))

        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID","Nome","Espécie","Raça","Idade","Porte","Gênero","Status","Abrigo"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        for c,w in (("ID",50),("Nome",140),("Espécie",100),("Raça",120),("Idade",60),
                    ("Porte",80),("Gênero",80),("Status",100),("Abrigo",120)):
            self.tree.heading(c,text=c.upper())
            self.tree.column(c,width=w,anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Right panel - Formulário
        right_panel = ttk.Frame(self, width=400)
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

        # Campos do formulário
        r = 0
        self.inputs = {}
        fields = [
            ("Nome *", ttk.Entry, {"width":30}),
            ("Espécie", ttk.Combobox, {"values":["Gato","Cachorro","Pássaro"],"state":"readonly","width":30}),
            ("Raça", ttk.Entry, {"width":30}),
            ("Idade", ttk.Entry, {"width":30}),
            ("Porte", ttk.Combobox, {"values":SIZES,"state":"readonly","width":30}),
            ("Gênero", ttk.Combobox, {"values":GENDERS,"state":"readonly","width":30}),
            ("Status", ttk.Combobox, {"values":["Disponível","Em processo","Adotado","Indisponível"],"state":"readonly","width":30}),
            ("Temperamento", ttk.Combobox, {"values":["Calmo","Agitado","Ativo","Estressado"],"state":"readonly","width":30}),
            ("Abrigo", ttk.Combobox, {"values": self.get_shelters(), "state":"readonly","width":30}),  # NOVO CAMPO
        ]

        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r,column=0,columnspan=2,sticky="w", pady=(5,0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r,column=0,columnspan=2,sticky="we", pady=(0,5))
            self.inputs[label_text] = w
            r += 1

        # Observações
        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r,column=0,columnspan=2,sticky="w", pady=(5,0))
        r += 1
        self.inputs["Observações"] = tk.Text(self.scrollable_frame, height=4, width=30)
        self.inputs["Observações"].grid(row=r,column=0,columnspan=2,sticky="we", pady=(0,5))
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

    def get_shelters(self):
        """
        Obtém a lista de abrigos para popular o combobox.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para todos os abrigos
        """
        from models import Shelter
        return [f"{s.id} - {s.name}" for s in session.query(Shelter).all()]

    def load(self):
        """
        Carrega todos os animais na lista.
        
        Atualiza automaticamente o status se houver adoção finalizada
        e atualiza a lista de abrigos no combobox.
        """
        for i in self.tree.get_children():
            self.tree.delete(i)
        animals = session.query(Animal).order_by(Animal.id.desc()).all()
        for a in animals:
            # Atualiza status automaticamente se houver adoção finalizada
            finalized_adoption = any(ap.status=="Finalizado" for ap in a.adoptions)
            if finalized_adoption:
                a.status = "Adotado"
                
            # Obtém o nome do abrigo se existir
            shelter_name = a.shelter.name if a.shelter else ""
                
            self.tree.insert("", "end", iid=str(a.id),
                             values=(a.id, a.name, a.species, a.breed or "", a.age,
                                     a.size or "", a.gender or "", a.status, shelter_name))
        
        # Atualiza lista de abrigos no combobox
        self.inputs["Abrigo"]["values"] = self.get_shelters()
        session.commit()

    def on_select(self, event):
        """
        Manipula a seleção de um animal na lista.
        
        Args:
            event: Evento de seleção da Treeview
        """
        sel = self.tree.selection()
        if not sel: 
            return
            
        a = session.get(Animal, int(sel[0]))
        self.selected_id = a.id

        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, a.name or "")
        self.inputs["Espécie"].set(a.species or "")
        self.inputs["Raça"].delete(0, tk.END)
        self.inputs["Raça"].insert(0, a.breed or "")
        self.inputs["Idade"].delete(0, tk.END)
        self.inputs["Idade"].insert(0, a.age or 0)
        self.inputs["Porte"].set(a.size or "")
        self.inputs["Gênero"].set(a.gender or "")
        self.inputs["Status"].set(a.status or "")
        self.inputs["Temperamento"].set(a.temperament or "")
        
        # NOVO CAMPO - Abrigo
        if a.shelter:
            self.inputs["Abrigo"].set(f"{a.shelter.id} - {a.shelter.name}")
        else:
            self.inputs["Abrigo"].set("")
            
        self.inputs["Observações"].delete("1.0", tk.END)
        self.inputs["Observações"].insert(tk.END, a.health_history or "")

    def new(self):
        """Limpa o formulário para criar um novo animal."""
        self.selected_id = None
        for k, w in self.inputs.items():
            if isinstance(w, ttk.Combobox) or isinstance(w, tk.Text):
                if isinstance(w, tk.Text): 
                    w.delete("1.0", tk.END)
                else: 
                    w.set("")
            else:
                w.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um animal.
        
        Valida a capacidade do abrigo antes de salvar.
        """
        name = self.inputs["Nome *"].get().strip()
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return

        # VALIDAÇÃO DE CAPACIDADE DO ABRIGO (NOVA FUNCIONALIDADE)
        from models import Shelter
        shelter_val = self.inputs["Abrigo"].get().strip()
        if shelter_val:
            shelter_id = int(shelter_val.split(" - ")[0])
            shelter = session.get(Shelter, shelter_id)
            
            # Verificar capacidade do abrigo
            animais_atuais = session.query(Animal).filter(Animal.shelter_id == shelter_id).count()
            if animais_atuais >= shelter.capacity:
                messagebox.showerror("Erro", f"Abrigo '{shelter.name}' está lotado (capacidade: {shelter.capacity}).")
                return

        if self.selected_id:
            a = session.get(Animal, self.selected_id)
        else:
            a = Animal()
            session.add(a)

        a.name = name
        a.species = self.inputs["Espécie"].get()
        a.breed = self.inputs["Raça"].get().strip() or None
        try: 
            a.age = int(self.inputs["Idade"].get().strip())
        except: 
            a.age = 0
        a.size = self.inputs["Porte"].get()
        a.gender = self.inputs["Gênero"].get()
        a.status = self.inputs["Status"].get()
        a.temperament = self.inputs["Temperamento"].get()
        a.health_history = self.inputs["Observações"].get("1.0", tk.END).strip() or None
        
        # NOVO CAMPO - Abrigo
        if shelter_val:
            a.shelter_id = shelter_id
        else:
            a.shelter_id = None

        session.commit()
        self.load()
        messagebox.showinfo("Sucesso", "Animal salvo com sucesso.")

    def delete(self):
        """Exclui o animal selecionado após confirmação."""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um animal.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir animal selecionado?"):
            return
        a = session.get(Animal, self.selected_id)
        session.delete(a)
        session.commit()
        self.new()
        self.load()
        messagebox.showinfo("Sucesso", "Animal excluído com sucesso.")
