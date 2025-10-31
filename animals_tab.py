"""
Módulo de Gerenciamento de Animais - CRUD Completo
--------------------------------------------------
Este módulo fornece uma interface completa para gerenciar todos os animais
do sistema de abrigo. Implementa operações de Create, Read, Update e Delete
(CRUD) com validações robustas e interface intuitiva.

Funcionalidades principais:
- Cadastro completo de animais com todas as informações relevantes
- Listagem organizada com visualização em tabela scrollable
- Edição em tempo real de registros existentes
- Exclusão segura com confirmação
- Vinculação inteligente com abrigos
- Validação de capacidade dos abrigos
- Controle automático de status baseado em processos de adoção

Estrutura de dados gerenciada:
- Informações básicas: nome, espécie, raça, idade
- Características físicas: porte, gênero
- Status e saúde: status de adoção, temperamento, histórico de saúde
- Relacionamentos: abrigo vinculado, processos de adoção

Validações implementadas:
- Campos obrigatórios: nome do animal
- Validação numérica: idade deve ser um número inteiro
- Capacidade de abrigos: não permite superlotação
- Integridade referencial: mantém consistência com outras entidades
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal, AdoptionProcess
from utils import SIZES, GENDERS

class AnimalsTab(ttk.Frame):
    """
    Classe principal para gerenciamento de animais do abrigo.
    
    Esta classe implementa uma interface completa dividida em dois painéis:
    - Painel esquerdo: Lista de animais em formato de tabela
    - Painel direito: Formulário detalhado para cadastro/edição
    
    A interface oferece operações completas de CRUD com validações
    de negócio e integração com outras entidades do sistema.
    
    Atributos:
        selected_id (int): ID do animal atualmente selecionado para edição
        tree (ttk.Treeview): Componente de tabela para listagem
        inputs (dict): Dicionário com referências a todos os campos do formulário
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de animais com interface completa.
        
        Args:
            parent: Widget pai container (geralmente um Notebook)
            
        A construção da interface segue o padrão:
        1. Container principal com layout flexível
        2. Divisão em painel esquerdo (lista) e direito (formulário)
        3. Configuração da tabela com scrollbar
        4. Criação do formulário scrollable com todos os campos
        5. Adição de botões de ação
        6. Carregamento inicial dos dados
        """
        super().__init__(parent)
        
        # Configuração do layout principal
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== PAINEL ESQUERDO - LISTA DE ANIMAIS ==========
        left_panel = ttk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título da seção de listagem
        ttk.Label(left_panel, text="Lista de Animais", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela com sistema de scroll
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical para navegação na lista
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela para exibição dos animais
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "Espécie", "Raça", "Idade", "Porte", "Gênero", "Status", "Abrigo"),
            show="headings",  # Mostra apenas cabeçalhos, não a coluna #0
            yscrollcommand=scrollbar.set,
            height=20  # Altura fixa para 20 linhas visíveis
        )
        
        # Conexão da scrollbar com a tabela
        scrollbar.config(command=self.tree.yview)

        # Configuração detalhada das colunas
        columns_config = [
            ("ID", 50), ("Nome", 140), ("Espécie", 100), ("Raça", 120), 
            ("Idade", 60), ("Porte", 80), ("Gênero", 80), ("Status", 100), ("Abrigo", 120)
        ]
        
        for column_name, width in columns_config:
            self.tree.heading(column_name, text=column_name.upper())
            self.tree.column(column_name, width=width, anchor=tk.W)

        # Posicionamento da tabela
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vinculação do evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ========== PAINEL DIREITO - FORMULÁRIO DETALHADO ==========
        right_panel = ttk.Frame(self, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)  # Mantém largura fixa

        # Título do formulário
        ttk.Label(right_panel, text="Detalhes do Animal", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Container scrollable para o formulário
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        # Implementação de scroll para formulários longos
        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Configuração do sistema de scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        # Posicionamento dos componentes de scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        # ========== CAMPOS DO FORMULÁRIO ==========
        r = 0  # Contador de linhas para grid layout
        self.inputs = {}  # Dicionário para armazenar referências dos campos
        
        # Definição dos campos do formulário
        fields = [
            ("Nome *", ttk.Entry, {"width": 30}),
            ("Espécie", ttk.Combobox, {"values": ["Gato", "Cachorro", "Pássaro"], "state": "readonly", "width": 30}),
            ("Raça", ttk.Entry, {"width": 30}),
            ("Idade", ttk.Entry, {"width": 30}),
            ("Porte", ttk.Combobox, {"values": SIZES, "state": "readonly", "width": 30}),
            ("Gênero", ttk.Combobox, {"values": GENDERS, "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ["Disponível", "Em processo", "Adotado", "Indisponível"], "state": "readonly", "width": 30}),
            ("Temperamento", ttk.Combobox, {"values": ["Calmo", "Agitado", "Ativo", "Estressado", "Brincalhão", "Dócil"], "state": "readonly", "width": 30}),
            ("Abrigo", ttk.Combobox, {"values": self.get_shelters(), "state": "readonly", "width": 30}),
        ]

        # Criação dinâmica dos campos
        for label_text, widget_class, opts in fields:
            # Label descritivo do campo
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
            r += 1
            
            # Widget de entrada propriamente dito
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w  # Armazena referência
            r += 1

        # Campo de observações (área de texto multi-linha)
        ttk.Label(self.scrollable_frame, text="Observações").grid(row=r, column=0, columnspan=2, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Observações"] = tk.Text(self.scrollable_frame, height=4, width=30)
        self.inputs["Observações"].grid(row=r, column=0, columnspan=2, sticky="we", pady=(0, 5))
        r += 1

        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, columnspan=2, pady=10)
        
        # Botões com suas respectivas funções
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar Página", command=self.load).pack(side=tk.LEFT, padx=4)

        # ========== INICIALIZAÇÃO ==========
        self.selected_id = None  # Nenhum animal selecionado inicialmente
        self.load()  # Carrega dados iniciais

    def get_shelters(self):
        """
        Obtém a lista de abrigos disponíveis para popular o combobox.
        
        Este método consulta o banco de dados para obter todos os abrigos
        cadastrados e formata a lista no padrão "ID - Nome" para exibição
        no combobox de seleção de abrigo.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para todos os abrigos
                 cadastrados no sistema.
                 
        Exemplo de retorno:
            ["1 - Abrigo Central", "2 - Abrigo Zona Norte", "3 - Abrigo Temporário"]
        """
        from models import Shelter
        # Consulta todos os abrigos e formata a lista
        return [f"{s.id} - {s.name}" for s in session.query(Shelter).all()]

    def load(self):
        """
        Carrega todos os animais do banco de dados na tabela.
        
        Este método realiza as seguintes operações:
        1. Limpa a tabela atual removendo todos os itens
        2. Consulta todos os animais ordenados por ID decrescente
        3. Para cada animal, verifica e atualiza automaticamente o status
           baseado em processos de adoção finalizados
        4. Insere cada animal na tabela com suas informações formatadas
        5. Atualiza a lista de abrigos no combobox
        6. Confirma as transações no banco
        
        A atualização automática de status garante que animais com adoções
        finalizadas tenham seu status atualizado para "Adotado" mesmo que
        não tenham sido editados manualmente.
        """
        # Limpeza completa da tabela atual
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Consulta todos os animais ordenados por ID decrescente (mais recentes primeiro)
        animals = session.query(Animal).order_by(Animal.id.desc()).all()
        
        for animal in animals:
            # Atualização automática de status: verifica se há adoção finalizada
            finalized_adoption = any(
                adoption_process.status == "Finalizado" 
                for adoption_process in animal.adoptions
            )
            
            # Se encontrou adoção finalizada, atualiza o status do animal
            if finalized_adoption:
                animal.status = "Adotado"
                
            # Obtém o nome do abrigo se existir vinculação
            shelter_name = animal.shelter.name if animal.shelter else ""
                
            # Insere o animal na tabela
            self.tree.insert("", "end", iid=str(animal.id),
                           values=(animal.id, animal.name, animal.species, animal.breed or "", 
                                   animal.age, animal.size or "", animal.gender or "", 
                                   animal.status, shelter_name))
        
        # Atualiza a lista de abrigos no combobox
        self.inputs["Abrigo"]["values"] = self.get_shelters()
        
        # Confirma as possíveis alterações de status
        session.commit()

    def on_select(self, event):
        """
        Manipula a seleção de um animal na lista.
        
        Quando o usuário seleciona um animal na tabela, este método:
        1. Obtém o ID do animal selecionado
        2. Busca os dados completos do animal no banco
        3. Preenche todos os campos do formulário com os dados
        4. Formata campos especiais como abrigo e observações
        
        Args:
            event: Evento de seleção da Treeview (não utilizado diretamente)
        """
        # Obtém a seleção atual
        sel = self.tree.selection()
        if not sel:  # Se não há seleção, retorna silenciosamente
            return
            
        # Busca o animal selecionado no banco
        animal = session.get(Animal, int(sel[0]))
        self.selected_id = animal.id  # Armazena o ID para operações futuras

        # Preenche campos básicos do formulário
        self.inputs["Nome *"].delete(0, tk.END)
        self.inputs["Nome *"].insert(0, animal.name or "")
        
        self.inputs["Espécie"].set(animal.species or "")
        
        self.inputs["Raça"].delete(0, tk.END)
        self.inputs["Raça"].insert(0, animal.breed or "")
        
        self.inputs["Idade"].delete(0, tk.END)
        self.inputs["Idade"].insert(0, animal.age or 0)
        
        self.inputs["Porte"].set(animal.size or "")
        self.inputs["Gênero"].set(animal.gender or "")
        self.inputs["Status"].set(animal.status or "")
        self.inputs["Temperamento"].set(animal.temperament or "")
        
        # Campo Abrigo - formata para o padrão "ID - Nome"
        if animal.shelter:
            self.inputs["Abrigo"].set(f"{animal.shelter.id} - {animal.shelter.name}")
        else:
            self.inputs["Abrigo"].set("")
            
        # Campo Observações (área de texto)
        self.inputs["Observações"].delete("1.0", tk.END)
        self.inputs["Observações"].insert(tk.END, animal.health_history or "")

    def new(self):
        """
        Prepara o formulário para cadastrar um novo animal.
        
        Esta função limpa todos os campos do formulário e redefine
        o estado para permitir o cadastro de um novo animal.
        """
        self.selected_id = None  # Indica que é um novo registro
        
        # Limpa todos os campos do formulário
        for field_name, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")  # Limpa combobox
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)  # Limpa área de texto
            else:
                widget.delete(0, tk.END)  # Limpa campos de entrada

    def save(self):
        """
        Salva ou atualiza um animal no banco de dados.
        
        Esta função realiza as seguintes operações:
        1. Validação dos campos obrigatórios
        2. Validação da capacidade do abrigo selecionado
        3. Determinação se é criação ou edição
        4. Atualização dos dados do animal
        5. Commit das alterações no banco
        6. Recarregamento da lista
        
        Validações realizadas:
        - Nome do animal é obrigatório
        - Idade deve ser conversível para inteiro
        - Abrigo selecionado deve ter capacidade disponível
        """
        # Validação do campo obrigatório: nome
        name = self.inputs["Nome *"].get().strip()
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório.")
            return

        # VALIDAÇÃO DE CAPACIDADE DO ABRIGO
        from models import Shelter
        shelter_val = self.inputs["Abrigo"].get().strip()
        
        if shelter_val:
            # Extrai o ID do abrigo do formato "ID - Nome"
            shelter_id = int(shelter_val.split(" - ")[0])
            shelter = session.get(Shelter, shelter_id)
            
            # Verificação crítica de capacidade
            animais_atuais = session.query(Animal).filter(Animal.shelter_id == shelter_id).count()
            if animais_atuais >= shelter.capacity:
                messagebox.showerror("Erro", f"Abrigo '{shelter.name}' está lotado (capacidade: {shelter.capacity}).")
                return

        # Determina se é criação ou edição
        if self.selected_id:
            animal = session.get(Animal, self.selected_id)
        else:
            animal = Animal()
            session.add(animal)

        # Atualização dos dados básicos
        animal.name = name
        animal.species = self.inputs["Espécie"].get()
        animal.breed = self.inputs["Raça"].get().strip() or None
        
        # Processamento da idade com tratamento de erro
        try: 
            animal.age = int(self.inputs["Idade"].get().strip())
        except: 
            animal.age = 0  # Valor padrão em caso de erro
            
        animal.size = self.inputs["Porte"].get()
        animal.gender = self.inputs["Gênero"].get()
        animal.status = self.inputs["Status"].get()
        animal.temperament = self.inputs["Temperamento"].get()
        animal.health_history = self.inputs["Observações"].get("1.0", tk.END).strip() or None
        
        # Vinculação com abrigo
        if shelter_val:
            animal.shelter_id = shelter_id
        else:
            animal.shelter_id = None

        # Persistência no banco
        session.commit()
        self.load()  # Recarrega a lista
        messagebox.showinfo("Sucesso", "Animal salvo com sucesso.")

    def delete(self):
        """
        Exclui o animal selecionado após confirmação do usuário.
        
        Esta função implementa uma exclusão segura com as etapas:
        1. Verifica se há animal selecionado
        2. Solicita confirmação explícita do usuário
        3. Executa a exclusão no banco de dados
        4. Limpa o formulário e recarrega a lista
        
        A exclusão é irreversível e remove permanentemente o registro
        do animal do sistema.
        """
        # Verificação de seleção
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um animal.")
            return
            
        # Confirmação de segurança
        if not messagebox.askyesno("Confirmar", "Excluir animal selecionado?"):
            return
            
        # Execução da exclusão
        animal = session.get(Animal, self.selected_id)
        session.delete(animal)
        session.commit()
        
        # Limpeza e atualização da interface
        self.new()
        self.load()
        messagebox.showinfo("Sucesso", "Animal excluído com sucesso.")