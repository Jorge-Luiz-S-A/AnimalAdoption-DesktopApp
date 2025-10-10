# Aplicação principal

import tkinter as tk
from tkinter import ttk

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Abrigo")
        self.geometry("800x600")
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
