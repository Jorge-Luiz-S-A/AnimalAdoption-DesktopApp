"""
Módulo de Pesquisa Avançada de Animais - Sistema de Filtros
-----------------------------------------------------------
Este módulo fornece uma interface poderosa para busca e filtragem de animais
no sistema do abrigo. Permite encontrar animais específicos baseado em múltiplos
critérios de busca combinados.

Funcionalidades de busca:
- Filtro por espécie (busca parcial por texto)
- Filtro por porte (seleção em combobox)
- Filtro por localização (busca parcial por texto)
- Filtro por faixa etária (idade mínima e máxima)
- Combinação de múltiplos filtros simultaneamente

Características da interface:
- Formulário de filtros organizado e intuitivo
- Resultados em tabela com scroll
- Contador de resultados encontrados
- Limpeza rápida de filtros
- Layout responsivo e user-friendly

Técnicas de busca implementadas:
- Busca por texto parcial (LIKE %texto%)
- Filtros exatos para campos categóricos
- Faixas numéricas para idade
- Combinação de critérios com AND
"""

import tkinter as tk
from tkinter import ttk
from base_tab import BaseTab
from database import session
from models import Animal, Shelter
from utils import SIZES, parse_int, SPECIES

class SearchTab(BaseTab):
    """
    Classe para pesquisa avançada e filtragem de animais.
    
    Esta classe herda de BaseTab para aproveitar os estilos e métodos
    utilitários, e implementa um sistema completo de busca com múltiplos
    critérios combináveis.
    
    A interface é dividida em:
    - Seção superior: Formulário de filtros
    - Seção inferior: Tabela de resultados
    
    Atributos:
        e_species, e_location, e_amin, e_amax (ttk.Entry): Campos de texto
        cb_size (ttk.Combobox): Seletor de porte
        tree (ttk.Treeview): Tabela de resultados
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de pesquisa com todos os componentes.
        
        Args:
            parent: Widget pai container
            
        A construção segue a estrutura:
        1. Container principal com padding
        2. Seção de filtros com LabelFrame
        3. Dois níveis de organização para os campos
        4. Tabela de resultados com scrollbar
        5. Botões de ação (Buscar, Limpar)
        """
        super().__init__(parent)
        
        # Configuração do layout principal
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== SEÇÃO DE FILTROS ==========
        filt = ttk.LabelFrame(self, text="Filtros de Busca")
        filt.pack(fill=tk.X, padx=5, pady=5)

        # Primeira linha de filtros (espécie, porte, localização)
        filt_row1 = ttk.Frame(filt)
        filt_row1.pack(fill=tk.X, padx=10, pady=10)

        # Filtro: Espécie (combobox com espécies disponíveis em utils)
        ttk.Label(filt_row1, text="Espécie").grid(row=0, column=0, padx=(0, 5))
        self.cb_species = ttk.Combobox(filt_row1, values=SPECIES, state="readonly", width=16)
        self.cb_species.grid(row=0, column=1, padx=(0, 15))

        # Filtro: Porte (combobox com valores disponíveis em utils)
        ttk.Label(filt_row1, text="Porte").grid(row=0, column=2, padx=(0, 5))
        self.cb_size = ttk.Combobox(filt_row1, values=SIZES, state="readonly", width=14)
        self.cb_size.grid(row=0, column=3, padx=(0, 15))

        # Filtro: Abrigo (combobox com abrigos cadastrados no sistema)
        ttk.Label(filt_row1, text="Abrigo").grid(row=0, column=4, padx=(0, 5))
        self.cb_shelter = ttk.Combobox(filt_row1, values=self.get_shelters(), state="readonly", width=18)
        self.cb_shelter.grid(row=0, column=5)

        # Segunda linha de filtros (idade mínima/máxima e botões)
        filt_row2 = ttk.Frame(filt)
        filt_row2.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Filtro: Idade mínima
        ttk.Label(filt_row2, text="Idade mínima").grid(row=0, column=0, padx=(0, 5))
        self.e_amin = ttk.Entry(filt_row2, width=8)
        self.e_amin.grid(row=0, column=1, padx=(0, 15))

        # Filtro: Idade máxima
        ttk.Label(filt_row2, text="Idade máxima").grid(row=0, column=2, padx=(0, 5))
        self.e_amax = ttk.Entry(filt_row2, width=8)
        self.e_amax.grid(row=0, column=3, padx=(0, 15))

        # Botões de ação
        ttk.Button(filt_row2, text="Buscar", command=self.search, style="Success.TButton").grid(row=0, column=4, padx=(0, 5))
        ttk.Button(filt_row2, text="Limpar", command=self.clear_filters).grid(row=0, column=5)

        # ========== SEÇÃO DE RESULTADOS ==========
        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Título da seção de resultados
        ttk.Label(results_frame, text="Resultados da Busca", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela com scrollbar
        table_frame = ttk.Frame(results_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela de resultados
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "Espécie", "Idade", "Porte", "Gênero", "Status", "Abrigo"),
            show="headings", 
            height=14,  # Altura para 14 linhas
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        # Configuração das colunas da tabela
        columns_config = [
            ("ID", 60), ("Nome", 140), ("Espécie", 100), ("Idade", 60), 
            ("Porte", 80), ("Gênero", 80), ("Status", 100), ("Abrigo", 140)
        ]
        
        for column_name, width in columns_config:
            self.tree.heading(column_name, text=column_name.upper())
            self.tree.column(column_name, width=width, anchor=tk.W)

        # Posicionamento da tabela
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def clear_filters(self):
        """
        Limpa todos os campos de filtro e a tabela de resultados.
        
        Esta função restaura a interface ao estado inicial, permitindo
        que o usuário comece uma nova busca do zero.
        """
        # Limpa todos os campos de entrada
        # Limpa comboboxes e campos
        self.cb_species.set("")
        self.cb_size.set("")
        self.cb_shelter.set("")
        self.e_amin.delete(0, tk.END)
        self.e_amax.delete(0, tk.END)
        
        # Limpa a tabela de resultados
        for i in self.tree.get_children():
            self.tree.delete(i)

    def search(self):
        """
        Executa a busca com base nos filtros aplicados.
        
        Este método constrói uma consulta dinâmica ao banco de dados
        aplicando os filtros especificados pelo usuário. Os filtros
        são combinados com operador AND.
        
        A função realiza:
        1. Coleta dos valores dos filtros
        2. Construção incremental da query SQLAlchemy
        3. Aplicação dos filtros de texto (busca parcial)
        4. Aplicação dos filtros numéricos (faixa etária)
        5. Execução da consulta e exibição dos resultados
        6. Exibição do contador de resultados
        
        Técnicas de filtragem:
        - Combobox: filtro exato quando selecionado
        - Números: filtro por faixa (>= e <=)
        """
        # Inicia a query base
        query = session.query(Animal)

        # Coleta e limpa os valores dos filtros
        species = self.cb_species.get().strip()
        size = self.cb_size.get().strip()
        shelter_val = self.cb_shelter.get().strip()
        amin = self.e_amin.get().strip()
        amax = self.e_amax.get().strip()

        # Aplica filtro de espécie (busca parcial)
        if species:
            # Espécie vem do combobox (valores exatos)
            query = query.filter(Animal.species.ilike(f"%{species}%"))
            
        # Aplica filtro de porte (filtro exato)
        if size:
            query = query.filter(Animal.size.ilike(f"%{size}%"))
            
        # Aplica filtro de abrigo (filtro exato por ID extraído do combobox)
        if shelter_val:
            try:
                shelter_id = int(shelter_val.split(" - ")[0])
                query = query.filter(Animal.shelter_id == shelter_id)
            except Exception:
                # se parsing falhar, ignora o filtro
                pass
            
        # Aplica filtro de idade mínima
        if amin:
            query = query.filter(Animal.age >= parse_int(amin, 0))
            
        # Aplica filtro de idade máxima
        if amax:
            query = query.filter(Animal.age <= parse_int(amax, 9999))

        # Limpa resultados anteriores
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Executa a consulta e processa os resultados
        results = query.all()
        
        # Insere cada animal encontrado na tabela
        # Atualiza status localmente e mostra o nome do abrigo
        for animal in results:
            # Se houver adoção finalizada, marca como Adotado
            finalized_adoption = any(ap.status == "Finalizado" for ap in animal.adoptions)
            in_process = any(ap.status in ("Questionário", "Triagem", "Visita", "Documentos", "Aprovado") for ap in animal.adoptions)
            if finalized_adoption:
                animal.status = "Adotado"
            elif in_process:
                animal.status = "Em processo"

            shelter_name = animal.shelter.name if animal.shelter else ""

            # Insere apenas os 8 valores correspondentes às colunas
            # (ID, Nome, Espécie, Idade, Porte, Gênero, Status, Abrigo)
            self.tree.insert("", "end", values=(
                animal.id,
                animal.name,
                animal.species,
                animal.age,
                animal.size or "",
                animal.gender or "",
                animal.status,
                shelter_name
            ))

        # Persistir eventuais alterações de status
        session.commit()

        # Exibe o resumo da busca
        self.info(f"Encontrados {len(results)} animais.")

    def get_shelters(self):
        """
        Retorna a lista de abrigos cadastrados formatada para combobox.

        Formato: "{id} - {name}" como exibido em outras abas do sistema.
        """
        return [f"{s.id} - {s.name}" for s in session.query(Shelter).order_by(Shelter.id).all()]
