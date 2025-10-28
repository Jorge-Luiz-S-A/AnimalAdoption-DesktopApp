# search_tab.py
"""
Aba de pesquisa avançada de animais
"""
import tkinter as tk
from tkinter import ttk
from database import session
from models import Animal
from utils import SIZES, parse_int

class SearchTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(self, text="Filtros de Busca")
        filtros_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Primeira linha de filtros
        linha1 = ttk.Frame(filtros_frame)
        linha1.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(linha1, text="Espécie:").grid(row=0, column=0, padx=(0, 5))
        self.especie_entry = ttk.Entry(linha1, width=18)
        self.especie_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(linha1, text="Porte:").grid(row=0, column=2, padx=(0, 5))
        self.porte_combo = ttk.Combobox(linha1, values=SIZES, state="readonly", width=14)
        self.porte_combo.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(linha1, text="Localização:").grid(row=0, column=4, padx=(0, 5))
        self.local_entry = ttk.Entry(linha1, width=18)
        self.local_entry.grid(row=0, column=5)
        
        # Segunda linha de filtros
        linha2 = ttk.Frame(filtros_frame)
        linha2.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(linha2, text="Idade mínima:").grid(row=0, column=0, padx=(0, 5))
        self.idade_min_entry = ttk.Entry(linha2, width=8)
        self.idade_min_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(linha2, text="Idade máxima:").grid(row=0, column=2, padx=(0, 5))
        self.idade_max_entry = ttk.Entry(linha2, width=8)
        self.idade_max_entry.grid(row=0, column=3, padx=(0, 15))
        
        # Botões
        ttk.Button(linha2, text="Buscar", command=self.buscar).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(linha2, text="Limpar", command=self.limpar_filtros).grid(row=0, column=5)
        
        # Resultados
        resultados_frame = ttk.Frame(self)
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(resultados_frame, text="Resultados da Busca", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Tabela de resultados
        table_frame = ttk.Frame(resultados_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "Espécie", "Idade", "Porte", "Gênero", "Status", "Localização"),
            show="headings",
            height=14,
            yscrollcommand=scrollbar.set
        )
        
        scrollbar.config(command=self.tree.yview)
        
        colunas = [
            ("ID", 60), ("Nome", 140), ("Espécie", 100), ("Idade", 60),
            ("Porte", 80), ("Gênero", 80), ("Status", 100), ("Localização", 120)
        ]
        
        for col, width in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def buscar(self):
        """Executa busca com filtros"""
        # Coleta filtros
        especie = self.especie_entry.get().strip()
        porte = self.porte_combo.get().strip()
        localizacao = self.local_entry.get().strip()
        idade_min = self.idade_min_entry.get().strip()
        idade_max = self.idade_max_entry.get().strip()
        
        # Constrói query
        query = session.query(Animal)
        
        if especie:
            query = query.filter(Animal.species.ilike(f"%{especie}%"))
        
        if porte:
            query = query.filter(Animal.size.ilike(f"%{porte}%"))
        
        if localizacao:
            query = query.filter(Animal.location.ilike(f"%{localizacao}%"))
        
        if idade_min:
            query = query.filter(Animal.age >= parse_int(idade_min, 0))
        
        if idade_max:
            query = query.filter(Animal.age <= parse_int(idade_max, 999))
        
        # Limpa resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Executa busca
        animais = query.all()
        
        # Preenche resultados
        for animal in animais:
            self.tree.insert("", "end", values=(
                animal.id,
                animal.name,
                animal.species,
                animal.age,
                animal.size or "",
                animal.gender or "",
                animal.status,
                animal.location or ""
            ))
        
        # Mostra contagem
        self.mostrar_info(f"Encontrados {len(animais)} animais")
    
    def limpar_filtros(self):
        """Limpa todos os filtros"""
        self.especie_entry.delete(0, tk.END)
        self.porte_combo.set("")
        self.local_entry.delete(0, tk.END)
        self.idade_min_entry.delete(0, tk.END)
        self.idade_max_entry.delete(0, tk.END)
        
        # Limpa resultados
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        from tkinter import messagebox
        messagebox.showinfo("Busca", mensagem)
