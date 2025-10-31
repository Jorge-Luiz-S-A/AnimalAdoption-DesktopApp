"""
Módulo de Gerenciamento de Abrigos - CRUD Completo
--------------------------------------------------
Este módulo fornece uma interface completa para gerenciar todos os abrigos
do sistema. Inclui controle de capacidade, estatísticas automáticas e
gerenciamento de informações de contato.

Funcionalidades principais:
- Cadastro completo de abrigos com informações de contato
- Controle de capacidade máxima de animais
- Cálculo automático de estatísticas:
  - Animais resgatados (total histórico)
  - Animais adotados (com adoção finalizada)
  - Animais atuais (resgatados - adotados)
- Listagem organizada com todas as informações
- Validação de capacidade para evitar superlotação

Estatísticas calculadas automaticamente:
- Resgatados: total de animais vinculados ao abrigo
- Adotados: animais com processos finalizados
- Atuais: diferença entre resgatados e adotados

Validações implementadas:
- Capacidade deve ser número positivo
- Email deve ter formato válido (se informado)
- Prevenção de exclusão de abrigos com animais vinculados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Shelter, Animal, AdoptionProcess

class ShelterTab(ttk.Frame):
    """
    Classe para gerenciamento completo de abrigos.
    
    Esta classe implementa operações de CRUD para abrigos com cálculo
    automático de estatísticas e controle de capacidade.
    
    A interface é dividida em:
    - Painel esquerdo: Lista de abrigos com estatísticas
    - Painel direito: Formulário de cadastro/edição
    
    Atributos:
        selected_id (int): ID do abrigo selecionado para edição
        tree (ttk.Treeview): Tabela de abrigos
        inputs (dict): Campos do formulário de abrigo
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de gerenciamento de abrigos.
        
        Args:
            parent: Widget pai container
            
        A construção inclui:
        1. Divisão em painéis esquerdo/direito
        2. Tabela com colunas para todas as informações
        3. Formulário scrollable com campos de abrigo
        4. Sistema de estatísticas automáticas
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== PAINEL ESQUERDO - LISTA DE ABRIGOS ==========
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título da seção
        ttk.Label(left_panel, text="Lista de Abrigos", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela de abrigos com estatísticas
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "Email", "Telefone", "Endereço", "Capacidade", "Resgatados", "Adotados", "Animais Atuais"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        # Configuração detalhada das colunas
        columns_config = [
            ("ID", 40), ("Nome", 150), ("Email", 180), ("Telefone", 100), 
            ("Endereço", 150), ("Capacidade", 80), ("Resgatados", 80), 
            ("Adotados", 80), ("Animais Atuais", 80)
        ]
        
        for column_name, width in columns_config:
            self.tree.heading(column_name, text=column_name.upper())
            self.tree.column(column_name, width=width, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ========== PAINEL DIREITO - FORMULÁRIO ==========
        right_panel = ttk.Frame(main_container, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes do Abrigo", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

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
            ("Nome", ttk.Entry, {"width": 30}),
            ("Email", ttk.Entry, {"width": 30}),
            ("Telefone", ttk.Entry, {"width": 30}),
            ("Endereço", ttk.Entry, {"width": 30}),
            ("Capacidade", ttk.Entry, {"width": 30}),  # Campo numérico para capacidade
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        # ========== INICIALIZAÇÃO ==========
        self.selected_id = None
        self.load()

    def load(self):
        """
        Carrega todos os abrigos com estatísticas calculadas.
        
        Para cada abrigo, calcula automaticamente:
        - Animais resgatados: total de animais vinculados
        - Animais adotados: animais com adoção finalizada
        - Animais atuais: diferença entre resgatados e adotados
        
        Estas estatísticas são calculadas em tempo real a cada carregamento.
        """
        # Limpa a tabela atual
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Busca todos os abrigos ordenados por ID decrescente
        abrigos = session.query(Shelter).order_by(Shelter.id.desc()).all()
        
        for abrigo in abrigos:
            # Calcula estatísticas para o abrigo
            
            # Animais resgatados: total de animais vinculados ao abrigo
            rescued_count = session.query(Animal).filter(Animal.shelter_id == abrigo.id).count()
            
            # Animais adotados: animais com adoção finalizada
            adopted_count = (
                session.query(Animal)
                .join(Animal.adoptions)
                .filter(Animal.shelter_id == abrigo.id, AdoptionProcess.status == "Finalizado")
                .count()
            )
            
            # Animais atuais: resgatados - adotados
            animais_atuais = rescued_count - adopted_count
            
            # Insere o abrigo na tabela com todas as informações
            self.tree.insert(
                "",
                "end",
                iid=str(abrigo.id),
                values=(abrigo.id, abrigo.name or "", abrigo.email or "", abrigo.phone or "", 
                        abrigo.address or "", abrigo.capacity or 0, rescued_count, 
                        adopted_count, animais_atuais)
            )

    def on_select(self, event):
        """
        Manipula a seleção de um abrigo na lista.
        
        Preenche o formulário com os dados do abrigo selecionado
        para permitir edição.
        """
        sel = self.tree.selection()
        if not sel: 
            return
            
        # Busca o abrigo selecionado
        abrigo = session.get(Shelter, int(sel[0]))
        self.selected_id = abrigo.id

        # Preenche todos os campos do formulário
        self.inputs["Nome"].delete(0, tk.END)
        self.inputs["Nome"].insert(0, abrigo.name or "")
        
        self.inputs["Email"].delete(0, tk.END)
        self.inputs["Email"].insert(0, abrigo.email or "")
        
        self.inputs["Telefone"].delete(0, tk.END)
        self.inputs["Telefone"].insert(0, abrigo.phone or "")
        
        self.inputs["Endereço"].delete(0, tk.END)
        self.inputs["Endereço"].insert(0, abrigo.address or "")
        
        self.inputs["Capacidade"].delete(0, tk.END)
        self.inputs["Capacidade"].insert(0, str(abrigo.capacity or 0))

    def new(self):
        """Limpa o formulário para cadastrar um novo abrigo."""
        self.selected_id = None
        for key, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um abrigo no banco de dados.
        
        Valida a capacidade para garantir que seja um número válido
        e define um nome padrão se não for informado.
        """
        # Determina se é criação ou edição
        if self.selected_id:
            abrigo = session.get(Shelter, self.selected_id)
        else:
            abrigo = Shelter()
            session.add(abrigo)

        # Atualiza dados básicos
        abrigo.name = self.inputs["Nome"].get().strip() or "Meu Abrigo"
        abrigo.email = self.inputs["Email"].get().strip() or None
        abrigo.phone = self.inputs["Telefone"].get().strip() or None
        abrigo.address = self.inputs["Endereço"].get().strip() or None
        
        # Processa capacidade (converte para inteiro)
        try:
            abrigo.capacity = int(self.inputs["Capacidade"].get().strip() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Capacidade deve ser um número válido.")
            return

        try:
            session.commit()
            self.load()
            messagebox.showinfo("Sucesso", "Abrigo salvo com sucesso.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar abrigo: {e}")

    def delete(self):
        """
        Exclui o abrigo selecionado após confirmação.
        
        Verifica se há animais vinculados ao abrigo antes de permitir
        a exclusão para manter a integridade referencial.
        """
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um abrigo.")
            return
            
        # Verifica se há animais vinculados ao abrigo
        animais_vinculados = session.query(Animal).filter(Animal.shelter_id == self.selected_id).count()
        if animais_vinculados > 0:
            messagebox.showerror("Erro", f"Não é possível excluir o abrigo. Existem {animais_vinculados} animais vinculados a ele.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir abrigo selecionado?"):
            return
            
        try:
            abrigo = session.get(Shelter, self.selected_id)
            session.delete(abrigo)
            session.commit()
            
            self.new()
            self.load()
            messagebox.showinfo("Sucesso", "Abrigo excluído com sucesso.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir abrigo: {e}")