# base_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Required.TLabel", foreground="red")
        self.style.configure("Success.TButton", foreground="green")

    def info(self, msg: str):
        messagebox.showinfo("Info", msg)

    def error(self, msg: str):
        messagebox.showerror("Erro", msg)

    def create_form_field(self, parent, label, row, required=False, tooltip=None):
        label_widget = ttk.Label(parent, text=label)
        if required:
            label_widget.configure(style="Required.TLabel")
        label_widget.grid(row=row, column=0, sticky="w", pady=(5, 2))
        return row + 1
