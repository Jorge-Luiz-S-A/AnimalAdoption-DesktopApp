# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

from database import session
from animals_tab import AnimalsTab
from users_tab import UsersTab
from adoptions_tab import AdoptionsTab
from search_tab import SearchTab
from shelter_tab import ShelterTab
from models import Shelter

#teste

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Abrigo Animal - Sistema de Gerenciamento")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Apply modern theme
        sv_ttk.set_theme("light")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        self.style.configure("Success.TButton", foreground="green")
        
        # Create notebook (tabs)
        nb = ttk.Notebook(self)
        
        self.animals_tab = AnimalsTab(nb)
        self.users_tab = UsersTab(nb)
        self.shelter_tab = ShelterTab(nb)
        self.search_tab = SearchTab(nb)
        self.adoptions_tab = AdoptionsTab(nb)
        # Nota: Outras abas seriam adicionadas aqui seguindo o mesmo padrão

        nb.add(self.animals_tab, text="🐾 Animais")
        nb.add(self.users_tab, text="👥 Usuários")
        nb.add(self.shelter_tab, text="🏠 Abrigo")
        nb.add(self.search_tab, text="🔍 Busca")
        nb.add(self.adoptions_tab, text="💝 Adoções")
       # nb.add(self.fosters_tab, text="🏡 Foster")
        
        nb.pack(fill=tk.BOTH, expand=True)

        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar, text="Sistema de Gerenciamento de Abrigo Animal - Desenvolvido para fins acadêmicos").pack(side=tk.LEFT, padx=5)
        
        # Menu
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Sair", command=self.destroy)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.config(menu=menubar)
        
    def show_about(self):
        about_text = "Sistema de Gerenciamento de Abrigo Animal\n\n" \
                    "Desenvolvido para fins acadêmicos\n" \
                    "Funcionalidades:\n" \
                    "- Gerenciamento de Animais\n" \
                    "- Gerenciamento de Usuários\n" \
                    "- Processos de Adoção\n" \
                    "- Lar Temporário (Foster)\n" \
                    "- Sistema de Buscas\n" \
                    "- Perfil do Abrigo"
        messagebox.showinfo("Sobre", about_text)

if __name__ == "__main__":
    app = App()
    app.mainloop()
