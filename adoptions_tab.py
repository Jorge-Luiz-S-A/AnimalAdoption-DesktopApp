"""
Módulo de Gerenciamento de Processos de Adoção - Fluxo Completo
---------------------------------------------------------------
Este módulo gerencia todo o ciclo de vida dos processos de adoção no sistema
do abrigo. Desde o questionário inicial até a finalização da adoção, com
controle de status e atualização automática dos animais.

Funcionalidades principais:
- Criação e acompanhamento de processos de adoção
- Controle de status com fluxo definido
- Registro de datas de visitas (online e presencial)
- Vinculação entre animais disponíveis e usuários aprovados
- Atualização automática do status dos animais
- Sistema de observações e notas do processo

Fluxo de status implementado:
1. Questionário → 2. Triagem → 3. Visita Online → 4. Visita Presencial → 
5. Documentos → 6. Aprovado → 7. Finalizado/Recusado

Validações de integridade:
- Só permite animais com status "Disponível"
- Só permite usuários com status "Aprovado"
- Atualização automática do animal quando adoção é finalizada
- Restauração do status do animal quando adoção é cancelada
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User
from utils import ADOPTION_STEPS

class AdoptionsTab(ttk.Frame):
    """
    Classe para gerenciamento completo de processos de adoção.
    
    Esta classe implementa uma interface dividida em:
    - Painel esquerdo: Lista de processos em andamento
    - Painel direito: Formulário detalhado do processo
    
    Oferece operações completas de CRUD com validações de negócio
    e integração automática com o status dos animais.
    
    Atributos:
        selected_id (int): ID do processo selecionado para edição
        tree (ttk.Treeview): Tabela de processos
        inputs (dict): Campos do formulário de processo
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de processos de adoção.
        
        Args:
            parent: Widget pai container
            
        A construção da interface inclui:
        1. Divisão em painéis esquerdo/direito
        2. Tabela de processos com scroll
        3. Formulário scrollable com todos os campos
        4. Sistema de datas para visitas
        5. Botões de ação
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== PAINEL ESQUERDO - LISTA DE ADOÇÕES ==========
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título da seção
        ttk.Label(left_panel, text="Lista de Adoções", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela de processos
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Animal", "Usuário", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        # Configuração das colunas
        for c, w in (("ID", 50), ("Animal", 150), ("Usuário", 150), ("Status", 120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ========== PAINEL DIREITO - FORMULÁRIO ==========
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes da Adoção", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Container scrollable do formulário
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Configuração do scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        # ========== CAMPOS DO FORMULÁRIO ==========
        r = 0
        fields = [
            ("Animal *", ttk.Combobox, {"values": self.get_animals(), "state": "readonly", "width": 30}),
            ("Usuário *", ttk.Combobox, {"values": self.get_users(), "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ADOPTION_STEPS, "state": "readonly", "width": 30}),
            ("Visita Online", ttk.Entry, {"width": 30}),  # Data no formato DD/MM/AAAA
            ("Visita Presencial", ttk.Entry, {"width": 30}),  # Data no formato DD/MM/AAAA
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        # Campo de observações
        ttk.Label(self.scrollable_frame, text="Notas").grid(row=r, column=0, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Notas"] = tk.Text(self.scrollable_frame, width=30, height=5, wrap="word")
        self.inputs["Notas"].grid(row=r, column=0, sticky="we", pady=(0, 5))
        r += 1

        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        # ========== INICIALIZAÇÃO ==========
        self.selected_id = None
        self.load()

    # ========== FUNÇÕES AUXILIARES ==========

    def get_animals(self):
        """
        Obtém lista de animais disponíveis para adoção.
        
        Filtra apenas animais com status "Disponível" para garantir
        que só animais realmente disponíveis apareçam na lista.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para animais disponíveis
        """
        # Filtra apenas animais com status "Disponível"
        animais_disponiveis = session.query(Animal).filter(
            Animal.status == "Disponível"
        ).all()
        
        return [f"{a.id} - {a.name}" for a in animais_disponiveis]
    
    def get_users(self):
        """
        Obtém lista de usuários aprovados para adoção.
        
        Filtra apenas usuários com approved = True para garantir
        que só usuários habilitados possam ser vinculados a processos.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para usuários aprovados
        """
        # Filtra apenas usuários aprovados
        usuarios_aprovados = session.query(User).filter(
            User.approved == True
        ).all()
        
        return [f"{u.id} - {u.name}" for u in usuarios_aprovados]

    # ========== OPERAÇÕES CRUD ==========

    def load(self):
        """
        Carrega todos os processos de adoção na tabela.
        
        Ordena os processos por ID decrescente (mais recentes primeiro)
        e atualiza as listas de animais e usuários nos comboboxes.
        """
        # Limpa a tabela atual
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Busca todos os processos ordenados por ID decrescente
        for adocao in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(adocao.id),
                           values=(adocao.id,
                                   adocao.animal.name if adocao.animal else "-",
                                   adocao.user.name if adocao.user else "-",
                                   adocao.status or "-"))

        # Atualiza as listas nos comboboxes
        self.inputs["Animal *"]["values"] = self.get_animals()
        self.inputs["Usuário *"]["values"] = self.get_users()

    def on_select(self, event):
        """
        Manipula a seleção de um processo na lista.
        
        Preenche o formulário com os dados do processo selecionado
        e formata as datas para exibição no padrão DD/MM/AAAA.
        """
        sel = self.tree.selection()
        if not sel:
            return
            
        # Busca o processo selecionado
        adocao = session.get(AdoptionProcess, int(sel[0]))
        self.selected_id = adocao.id

        # Preenche campos básicos
        self.inputs["Animal *"].set(f"{adocao.animal.id} - {adocao.animal.name}" if adocao.animal else "")
        self.inputs["Usuário *"].set(f"{adocao.user.id} - {adocao.user.name}" if adocao.user else "")
        self.inputs["Status"].set(adocao.status or "")
        
        # Preenche datas de visita (formatadas)
        self.inputs["Visita Online"].delete(0, tk.END)
        if adocao.virtual_visit_at:
            self.inputs["Visita Online"].insert(0, adocao.virtual_visit_at.strftime("%d/%m/%Y"))
            
        self.inputs["Visita Presencial"].delete(0, tk.END)
        if adocao.in_person_visit_at:
            self.inputs["Visita Presencial"].insert(0, adocao.in_person_visit_at.strftime("%d/%m/%Y"))
            
        # Preenche observações
        self.inputs["Notas"].delete("1.0", tk.END)
        self.inputs["Notas"].insert("1.0", adocao.notes or "")

    def new(self):
        """Limpa o formulário para criar um novo processo."""
        self.selected_id = None
        for key, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um processo de adoção.
        
        Realiza validações de campos obrigatórios e formato de datas,
        atualiza automaticamente o status do animal vinculado.
        """
        # Validações de campos obrigatórios
        animal_val = self.inputs["Animal *"].get().strip()
        user_val = self.inputs["Usuário *"].get().strip()

        if not animal_val or not user_val:
            messagebox.showerror("Erro", "Animal e Usuário são obrigatórios.")
            return

        # Extrai IDs dos valores do combobox
        animal_id = int(animal_val.split(" - ")[0])
        user_id = int(user_val.split(" - ")[0])

        # Determina se é criação ou edição
        if self.selected_id:
            adocao = session.get(AdoptionProcess, self.selected_id)
        else:
            adocao = AdoptionProcess()
            session.add(adocao)

        # Atualiza dados básicos
        adocao.animal_id = animal_id
        adocao.user_id = user_id
        adocao.status = self.inputs["Status"].get().strip() or None
        adocao.notes = self.inputs["Notas"].get("1.0", tk.END).strip() or None

        # Processa datas de visita com tratamento de erro
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
            # Salva o processo
            session.commit()
            
            # Atualiza automaticamente o status do animal
            adocao.update_animal_status()
            session.commit()
            
            self.load()
            messagebox.showinfo("Sucesso", "Adoção salva com sucesso. Status do animal atualizado automaticamente.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar adoção: {e}")

    def delete(self):
        """
        Exclui o processo de adoção selecionado.
        
        Antes de excluir, restaura o status do animal para "Disponível"
        para que ele possa aparecer em novos processos de adoção.
        """
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione uma adoção.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir adoção selecionada?"):
            return
            
        try:
            adocao = session.get(AdoptionProcess, self.selected_id)
            
            # Restaura o status do animal para disponível
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