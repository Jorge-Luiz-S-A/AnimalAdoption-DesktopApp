"""
Aba de Pesquisa - Busca avançada
--------------------------------
Permite buscar animais com base em diversos critérios de filtro.
"""

import tkinter as tk
from tkinter import ttk
from base_tab import BaseTab
from database import session
from models import Animal
from utils import SIZES, parse_int

class SearchTab(BaseTab):
    """
    Aba para pesquisa avançada de animais.
    
    Funcionalidades:
    - Filtrar animais por espécie, porte, localização, idade
    - Exibir resultados em tabela com scroll
    - Limpar filtros rapidamente
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de pesquisa.
        
        Args:
            parent: Widget pai onde a aba será inserida
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Filtros
        filt = ttk.LabelFrame(self, text="Filtros de Busca")
        filt.pack(fill=tk.X, padx=5, pady=5)

        # Primeira linha de filtros
        filt_row1 = ttk.Frame(filt)
        filt_row1.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(filt_row1, text="Espécie").grid(row=0, column=0, padx=(0,5))
        self.e_species = ttk.Entry(filt_row1, width=18)
        self.e_species.grid(row=0, column=1, padx=(0,15))

        ttk.Label(filt_row1, text="Porte").grid(row=0, column=2, padx=(0,5))
        self.cb_size = ttk.Combobox(filt_row1, values=SIZES, state="readonly", width=14)
        self.cb_size.grid(row=0, column=3, padx=(0,15))

        ttk.Label(filt_row1, text="Local").grid(row=0, column=4, padx=(0,5))
        self.e_location = ttk.Entry(filt_row1, width=18)
        self.e_location.grid(row=0, column=5)

        # Segunda linha de filtros
        filt_row2 = ttk.Frame(filt)
        filt_row2.pack(fill=tk.X, padx=10, pady=(0,10))

        ttk.Label(filt_row2, text="Idade mínima").grid(row=0, column=0, padx=(0,5))
        self.e_amin = ttk.Entry(filt_row2, width=8)
        self.e_amin.grid(row=0, column=1, padx=(0,15))

        ttk.Label(filt_row2, text="Idade máxima").grid(row=0, column=2, padx=(0,5))
        self.e_amax = ttk.Entry(filt_row2, width=8)
        self.e_amax.grid(row=0, column=3, padx=(0,15))

        ttk.Button(filt_row2, text="Buscar", command=self.search, style="Success.TButton").grid(row=0, column=4, padx=(0,5))
        ttk.Button(filt_row2, text="Limpar", command=self.clear_filters).grid(row=0, column=5)

        # Resultados
        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(results_frame, text="Resultados da Busca", style="Header.TLabel").pack(anchor=tk.W, pady=(0,5))

        # Tabela com scrollbar
        table_frame = ttk.Frame(results_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("id","name","species","age","size","gender","status","location"),
            show="headings", height=14, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        for c, w in (("id",60), ("name",140), ("species",100), ("age",60), ("size",80),
                     ("gender",80), ("status",100), ("location",120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def clear_filters(self):
        """Limpa todos os campos de filtro."""
        self.e_species.delete(0, tk.END)
        self.cb_size.set("")
        self.e_location.delete(0, tk.END)
        self.e_amin.delete(0, tk.END)
        self.e_amax.delete(0, tk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)

    def search(self):
        """
        Executa a busca com base nos filtros aplicados.
        
        Exibe os resultados na tabela e mostra contagem de animais encontrados.
        """
        q = session.query(Animal)

        species = self.e_species.get().strip()
        size = self.cb_size.get().strip()
        location = self.e_location.get().strip()
        amin = self.e_amin.get().strip()
        amax = self.e_amax.get().strip()

        if species:
            q = q.filter(Animal.species.ilike(f"%{species}%"))
        if size:
            q = q.filter(Animal.size.ilike(f"%{size}%"))
        if location:
            q = q.filter(Animal.location.ilike(f"%{location}%"))
        if amin:
            q = q.filter(Animal.age >= parse_int(amin, 0))
        if amax:
            q = q.filter(Animal.age <= parse_int(amax, 9999))

        # Limpa resultados anteriores
        for i in self.tree.get_children():
            self.tree.delete(i)

        results = q.all()
        for a in results:
            self.tree.insert("", "end", values=(
                a.id,
                a.name,
                a.species,
                a.age,
                a.size or "",
                a.gender or "",
                a.status,
                a.location or ""
            ))

        self.info(f"Encontrados {len(results)} animais.")
