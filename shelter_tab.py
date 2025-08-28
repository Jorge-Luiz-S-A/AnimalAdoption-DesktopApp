# shelter_tab.py
import tkinter as tk
from tkinter import ttk

from base_tab import BaseTab
from database import session
from models import Shelter
from utils import parse_int

class ShelterTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Perfil do Abrigo", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        r = 1
        r = self.create_form_field(form_frame, "Nome", r)
        self.e_name = ttk.Entry(form_frame, width=40); self.e_name.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Email", r)
        self.e_email = ttk.Entry(form_frame); self.e_email.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Telefone", r)
        self.e_phone = ttk.Entry(form_frame); self.e_phone.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Endereço", r)
        self.e_address = ttk.Entry(form_frame); self.e_address.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Autenticidade verificada", r)
        self.cb_auth = ttk.Combobox(form_frame, values=["", "Sim", "Não"], state="readonly"); self.cb_auth.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Resgatados (contagem)", r)
        self.e_rescued = ttk.Entry(form_frame); self.e_rescued.grid(row=r, column=1, sticky="we", pady=(0, 10)); r+=1

        r = self.create_form_field(form_frame, "Adotados (contagem)", r)
        self.e_adopted = ttk.Entry(form_frame); self.e_adopted.grid(row=r, column=1, sticky="we", pady=(0, 15)); r+=1

        ttk.Button(form_frame, text="Salvar", command=self.save, style="Success.TButton").grid(row=r, column=0, columnspan=2, pady=8)

        form_frame.columnconfigure(1, weight=1)
        self.load()

    def load(self):
        s = session.query(Shelter).first()
        if not s:
            s = Shelter(name="Meu Abrigo")
            session.add(s); session.commit()
        self.e_name.delete(0, tk.END); self.e_name.insert(0, s.name or "")
        self.e_email.delete(0, tk.END); self.e_email.insert(0, s.email or "")
        self.e_phone.delete(0, tk.END); self.e_phone.insert(0, s.phone or "")
        self.e_address.delete(0, tk.END); self.e_address.insert(0, s.address or "")
        self.cb_auth.set("Sim" if s.authenticity_verified else "Não")
        self.e_rescued.delete(0, tk.END); self.e_rescued.insert(0, str(s.rescued_count or 0))
        self.e_adopted.delete(0, tk.END); self.e_adopted.insert(0, str(s.adopted_count or 0))

    def save(self):
        s = session.query(Shelter).first()
        s.name = self.e_name.get().strip() or "Meu Abrigo"
        s.email = self.e_email.get().strip() or None
        s.phone = self.e_phone.get().strip() or None
        s.address = self.e_address.get().strip() or None
        s.authenticity_verified = (self.cb_auth.get() == "Sim")
        s.rescued_count = parse_int(self.e_rescued.get() or "0", 0)
        s.adopted_count = parse_int(self.e_adopted.get() or "0", 0)
        session.commit()
        self.info("Perfil do abrigo salvo com sucesso.")
