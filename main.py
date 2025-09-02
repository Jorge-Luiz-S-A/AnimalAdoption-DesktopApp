# main.py
import tkinter as tk
from tkinter import ttk
import sv_ttk

from animals_tab import AnimalsTab
from adoptions_tab import AdoptionsTab
from users_tab import UsersTab
from shelter_tab import ShelterTab
from search_tab import SearchTab
from database import init_db
from login import login_screen

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Animal Adoption Platform")
        self.geometry("1600x900")
        sv_ttk.set_theme("light")

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        notebook.add(AnimalsTab(notebook), text="Animals")
        notebook.add(AdoptionsTab(notebook), text="Adoptions")
        notebook.add(UsersTab(notebook), text="Users")
        notebook.add(ShelterTab(notebook), text="Shelter")
        notebook.add(SearchTab(notebook), text="Search")

if __name__ == "__main__":
    init_db()
    if login_screen():
        app = MainApp()
        app.mainloop()
    else:
        print("Login falhou. Encerrando aplicação.")
