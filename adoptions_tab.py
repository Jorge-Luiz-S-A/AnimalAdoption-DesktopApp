# adoptions_tab.py
"""
Aba para gerenciar processos de adoção
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User

class AdoptionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(self, text="Processos de Adoção", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de adoções
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Adoções em Andamento", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Animal", "Tutor", "Status"), show="headings", height=15)
        for col, width in [("ID", 50), ("Animal", 150), ("Tutor", 150), ("Status", 100)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Formulário
        form_frame = ttk.Frame(main_frame, width=300)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)
        form_frame.pack_propagate(False)
        
        ttk.Label(form_frame, text="Dados da Adoção", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Campos
        ttk.Label(form_frame, text="Animal:").pack(anchor=tk.W)
        self.animal_combo = ttk.Combobox(form_frame, state="readonly", width=27)
        self.animal_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Tutor:").pack(anchor=tk.W)
        self.user_combo = ttk.Combobox(form_frame, state="readonly", width=27)
        self.user_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Status:").pack(anchor=tk.W)
        self.status_combo = ttk.Combobox(form_frame, values=["Questionário", "Triagem", "Aprovado", "Finalizado"], state="readonly", width=27)
        self.status_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Observações:").pack(anchor=tk.W)
        self.notes_text = tk.Text(form_frame, height=4, width=30)
        self.notes_text.pack(fill=tk.X, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.novo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=5)
        
        self.selected_id = None
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega comboboxes e lista"""
        # Animais disponíveis
        animais = session.query(Animal).filter(Animal.status == "Disponível").all()
        self.animal_combo['values'] = [f"{a.id} - {a.name}" for a in animais]
        
        # Usuários aprovados
        usuarios = session.query(User).filter(User.approved == True).all()
        self.user_combo['values'] = [f"{u.id} - {u.name}" for u in usuarios]
        
        # Lista de adoções
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        adopcoes = session.query(AdoptionProcess).all()
        for adopcao in adopcoes:
            self.tree.insert("", "end", values=(
                adopcao.id,
                adopcao.animal.name if adopcao.animal else "-",
                adopcao.user.name if adopcao.user else "-",
                adopcao.status
            ))
    
    def on_select(self, event):
        """Quando seleciona uma adoção"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            
            adopcao = session.query(AdoptionProcess).get(self.selected_id)
            
            if adopcao.animal:
                self.animal_combo.set(f"{adopcao.animal.id} - {adopcao.animal.name}")
            if adopcao.user:
                self.user_combo.set(f"{adopcao.user.id} - {adopcao.user.name}")
                
            self.status_combo.set(adopcao.status)
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", adopcao.notes or "")
    
    def novo(self):
        """Nova adoção"""
        self.selected_id = None
        self.animal_combo.set("")
        self.user_combo.set("")
        self.status_combo.set("Questionário")
        self.notes_text.delete("1.0", tk.END)
    
    def salvar(self):
        """Salva adoção"""
        animal_val = self.animal_combo.get()
        user_val = self.user_combo.get()
        status = self.status_combo.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not animal_val or not user_val:
            messagebox.showerror("Erro", "Selecione animal e tutor!")
            return
        
        # Extrai IDs
        animal_id = int(animal_val.split(" - ")[0])
        user_id = int(user_val.split(" - ")[0])
        
        if self.selected_id:
            # Edição
            adopcao = session.query(AdoptionProcess).get(self.selected_id)
            adopcao.animal_id = animal_id
            adopcao.user_id = user_id
            adopcao.status = status
            adopcao.notes = notes
            mensagem = "Adoção atualizada!"
        else:
            # Nova
            adopcao = AdoptionProcess(animal_id=animal_id, user_id=user_id, status=status, notes=notes)
            session.add(adopcao)
            
            # Atualiza status do animal
            animal = session.query(Animal).get(animal_id)
            animal.status = "Em processo"
            mensagem = "Adoção criada!"
        
        session.commit()
        self.carregar_dados()
        self.novo()
        messagebox.showinfo("Sucesso", mensagem)
    
    def excluir(self):
        """Exclui adoção"""
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione uma adoção!")
            return
            
        if messagebox.askyesno("Confirmar", "Excluir adoção selecionada?"):
            adopcao = session.query(AdoptionProcess).get(self.selected_id)
            
            # Restaura status do animal
            if adopcao.animal:
                adopcao.animal.status = "Disponível"
            
            session.delete(adopcao)
            session.commit()
            self.carregar_dados()
            self.novo()
            messagebox.showinfo("Sucesso", "Adoção excluída!")
