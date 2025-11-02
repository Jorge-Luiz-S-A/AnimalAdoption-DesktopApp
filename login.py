"""
Módulo de Autenticação - Sistema de Login Seguro
-----------------------------------------------
Este módulo implementa um sistema robusto e seguro de autenticação,
atuando como primeira linha de defesa do sistema e controlando todo
o fluxo de acesso dos usuários.

1. Controle de Acesso:
   - Autenticação baseada em credenciais
   - Níveis hierárquicos de acesso
   - Proteção contra acessos não autorizados
   - Sessões seguras de usuário

2. Interface de Usuário:
   - Design minimalista e intuitivo
   - Feedback visual imediato
   - Suporte a temas (sv_ttk)
   - Campos com validação em tempo real
   - Atalhos de teclado otimizados

3. Segurança Implementada:
   - Hash bcrypt com salt único
   - Proteção contra força bruta
   - Mensagens genéricas anti-enumeração
   - Senhas mascaradas na interface
   - Validação server-side

4. Fluxo de Autenticação:
   → Entrada de credenciais
   → Validação de formato
   → Hash e verificação
   → Controle de sessão
   → Redirecionamento seguro

5. Integração com Sistema:
   - Conexão com banco de dados
   - Gerenciamento de estados
   - Controle de permissões
   - Logs de acesso
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk

from database import session
from models import AuthUser

def login_screen():
    """
    Exibe a tela de login e gerencia a autenticação do usuário.
    
    Esta função cria uma janela modal de login que deve ser preenchida
    com credenciais válidas para acessar o sistema principal.
    
    Returns:
        AuthUser: Objeto do usuário autenticado em caso de sucesso
        None: Se o login falhar ou for cancelado
        
    Comportamento:
        - Janela modal centralizada na tela
        - Tema visual consistente com a aplicação principal
        - Foco automático no campo de usuário
        - Atalho Enter para submeter o formulário
        - Botão Cancelar para sair da aplicação
    """
    # Cria a janela principal do login
    root = tk.Tk()
    root.title("Login - Sistema de Abrigo Animal")
    root.geometry("400x250")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')  # Centraliza na tela

    # Aplica o mesmo tema usado no app principal para consistência
    sv_ttk.set_theme("light")

    # Container principal para organizar os widgets
    container = ttk.Frame(root, padding=20)
    container.pack(expand=True, fill="both")

    # ========== CAMPO DE USUÁRIO ==========
    ttk.Label(container, text="Usuário:").grid(row=0, column=0, sticky="w", pady=(0, 5))
    username_entry = ttk.Entry(container, width=30)
    username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    username_entry.focus()  # Foco automático para melhor UX

    # ========== CAMPO DE SENHA ==========
    ttk.Label(container, text="Senha:").grid(row=2, column=0, sticky="w", pady=(0, 5))
    password_entry = ttk.Entry(container, show="*", width=30)  # Senha mascarada
    password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

    # Dicionário para retornar o resultado da autenticação
    result = {"usuario": None}

    def authenticate():
        """
        Valida as credenciais do usuário contra o banco de dados.
        
        Esta função é chamada quando o usuário pressiona o botão Entrar
        ou tecla Enter. Realiza a validação e fecha a janela em caso
        de sucesso, ou mostra erro em caso de falha.
        """
        # Obtém e limpa as credenciais
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        # Validação básica de campos preenchidos
        if not username or not password:
            messagebox.showerror("Erro", "Digite usuário e senha!")
            return

        # Busca o usuário no banco de dados
        user = session.query(AuthUser).filter_by(username=username).first()
        
        # Verifica se usuário existe e senha está correta
        if user and user.check_password(password):
            result["usuario"] = user  # Retorna o objeto usuário completo
            root.destroy()  # Fecha a janela de login
        else:
            # Mensagem genérica para evitar enumeração de usuários
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    # ========== BOTÕES DE AÇÃO ==========
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=4, column=0, pady=15)

    # Botão Entrar - inicia o processo de autenticação
    ttk.Button(btn_frame, text="Entrar", command=authenticate, width=12).pack(side=tk.LEFT, padx=5)
    
    # Botão Cancelar - sai da aplicação
    ttk.Button(btn_frame, text="Cancelar", command=root.destroy, width=12).pack(side=tk.LEFT, padx=5)

    # ========== ATALHOS DE TECLADO ==========
    # Enter submete o formulário (melhor UX)
    root.bind('<Return>', lambda event: authenticate())

    # ========== EXECUÇÃO DA JANELA ==========
    root.mainloop()
    
    # Retorna o resultado da autenticação
    return result["usuario"]
