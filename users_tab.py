# users_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import json

from base_tab import BaseTab
from database import session
from models import User, Animal
from utils import combobox_set

class UsersTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Table
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="Lista de Usuários", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Table with scrollbar
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame, columns=("ID","Nome","Email","Cidade","Aprovado"), 
                                show="headings", height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        for c, w in (("ID",60), ("Nome",160), ("Email",180), ("Cidade",120), ("Aprovado",90)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right panel - Form
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        ttk.Label(right_panel, text="Detalhes do Usuário", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Form container with scrollbar
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(form_container, height=500)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        r = 0
        r = self.create_form_field(scrollable_frame, "Nome *", r, True)
        self.e_name = ttk.Entry(scrollable_frame, width=32); self.e_name.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Email *", r, True)
        self.e_email = ttk.Entry(scrollable_frame); self.e_email.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Telefone", r)
        self.e_phone = ttk.Entry(scrollable_frame); self.e_phone.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Cidade", r)
        self.e_city = ttk.Entry(scrollable_frame); self.e_city.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(scrollable_frame, "Aprovado", r)
        self.cb_approved = ttk.Combobox(scrollable_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_approved.grid(row=r, column=0, sticky="we", pady=(0, 10)); r+=1

        # Buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=r, column=0, sticky="we", pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save, style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Atualizar", command=self.load).pack(side=tk.LEFT, padx=4)

        scrollable_frame.columnconfigure(0, weight=1)
        self.selected_id = None
        self.load()

    def load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for u in session.query(User).order_by(User.id.desc()).all():
            self.tree.insert("", "end", iid=str(u.id),
                             values=(u.id, u.name, u.email, u.city or "", "Sim" if u.approved else "Não"))

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        u = session.get(User, int(sel[0]))
        self.selected_id = u.id
        self.e_name.delete(0, tk.END); self.e_name.insert(0, u.name or "")
        self.e_email.delete(0, tk.END); self.e_email.insert(0, u.email or "")
        self.e_phone.delete(0, tk.END); self.e_phone.insert(0, u.phone or "")
        self.e_city.delete(0, tk.END); self.e_city.insert(0, u.city or "")
        self.cb_approved.set("Sim" if u.approved else "Não")

    def reload_favorites(self, u: User):
        self.lb_favs.delete(0, tk.END)
        for a in u.favorites:
            self.lb_favs.insert(tk.END, f"#{a.id} - {a.name} ({a.species})")

    def new(self):
        self.selected_id = None
        for e in (self.e_name, self.e_email, self.e_phone, self.e_city):
            e.delete(0, tk.END)
        self.cb_approved.set("")

    def save(self):
        name = self.e_name.get().strip()
        email = self.e_email.get().strip()
        if not name or not email:
            self.error("Nome e Email são obrigatórios.")
            return

        if self.selected_id:
            u = session.get(User, self.selected_id)
        else:
            u = User()
            session.add(u)

        u.name = name
        u.email = email
        u.phone = self.e_phone.get().strip() or None
        u.city = self.e_city.get().strip() or None
        u.approved = (self.cb_approved.get() == "Sim")

        session.commit()
        self.load()
        self.info("Usuário salvo com sucesso.")

    def delete(self):
        if not self.selected_id:
            self.error("Selecione um registro.")
            return
        if not messagebox.askyesno("Confirmar", "Excluir usuário selecionado?"):
            return
        u = session.get(User, self.selected_id)
        session.delete(u)
        session.commit()
        self.new()
        self.load()
        self.info("Usuário excluído com sucesso.")

    def add_favorite(self):
        if not self.selected_id:
            self.error("Selecione um usuário.")
            return
        
        win = tk.Toplevel(self)
        win.title("Adicionar Favorito")
        win.geometry("400x120")
        win.transient(self)
        win.grab_set()
        
        ttk.Label(win, text="Selecione o Animal").pack(padx=8, pady=6)
        animals = session.query(Animal).order_by(Animal.id.desc()).all()
        opts = [f"#{a.id} - {a.name} ({a.species})" for a in animals]
        cb = ttk.Combobox(win, values=opts, state="readonly", width=40)
        cb.pack(padx=8, pady=6)

        def do_add():
            idx = cb.current()
            if idx < 0:
                return
            u = session.get(User, self.selected_id)
            a = animals[idx]
            if a not in u.favorites:
                u.favorites.append(a)
                session.commit()
                self.reload_favorites(u)
                self.info(f"Animal #{a.id} adicionado aos favoritos.")
            win.destroy()

        ttk.Button(win, text="Adicionar", command=do_add).pack(pady=6)

    def remove_favorite(self):
        if not self.selected_id:
            self.error("Selecione um usuário.")
            return
        sel_idx = self.lb_favs.curselection()
        if not sel_idx:
            self.error("Selecione um favorito na lista.")
            return
        label = self.lb_favs.get(sel_idx[0])
        animal_id = int(label.split(" ")[0].replace("#",""))
        u = session.get(User, self.selected_id)
        a = session.get(Animal, animal_id)
        if a in u.favorites:
            u.favorites.remove(a)
            session.commit()
            self.reload_favorites(u)
            self.info(f"Animal #{a.id} removido dos favoritos.")
