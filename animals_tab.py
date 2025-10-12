# animals_tab.py
"""
Aba para gerenciar animais - primeira versão
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import Animal

class AnimalsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(self, text="Gerenciar Animais", font=("Arial", 12)).pack(pady=10)
        
        # Frame para botões
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Novo Animal", command=self.novo_animal).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Listar Animais", command=self.listar_animais).pack(side=tk.LEFT, padx=5)
        
        # Área para lista
        self.lista_frame = ttk.Frame(self)
        self.lista_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def novo_animal(self):
        """Abre janela para cadastrar novo animal"""
        janela = tk.Toplevel(self)
        janela.title("Novo Animal")
        janela.geometry("300x200")
        
        # Campos do formulário
        ttk.Label(janela, text="Nome:").pack(pady=5)
        nome_entry = ttk.Entry(janela, width=30)
        nome_entry.pack(pady=5)
        
        ttk.Label(janela, text="Espécie:").pack(pady=5)
        especie_entry = ttk.Entry(janela, width=30)
        especie_entry.pack(pady=5)
        
        def salvar():
            nome = nome_entry.get().strip()
            especie = especie_entry.get().strip()
            
            if nome and especie:
                # Salva no banco
                animal = Animal(name=nome, species=especie, age=0, status="Disponível")
                session.add(animal)
                session.commit()
                messagebox.showinfo("Sucesso", "Animal salvo!")
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Preencha todos os campos!")
        
        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=10)
    
    def listar_animais(self):
        """Mostra lista de animais"""
        # Limpa frame anterior
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        # Busca animais do banco
        animais = session.query(Animal).all()
        
        if animais:
            ttk.Label(self.lista_frame, text="Animais Cadastrados:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            for animal in animais:
                texto = f"{animal.id}: {animal.name} - {animal.species} ({animal.status})"
                ttk.Label(self.lista_frame, text=texto).pack(anchor=tk.W)
        else:
            ttk.Label(self.lista_frame, text="Nenhum animal cadastrado").pack()