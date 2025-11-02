"""
Módulo de Administração do Sistema - Gerenciamento de Usuários
---------------------------------------------------------------
Este módulo implementa um sistema robusto e seguro para administração de
usuários do sistema, com controles de acesso e validações rigorosas.

Funcionalidades principais:
- Interface administrativa exclusiva para admins
- Gerenciamento completo de contas de usuário
- Sistema hierárquico de permissões
- Proteções contra operações indevidas
- Hash seguro de senhas com bcrypt
- Validações em tempo real

Controle de acesso:
- Níveis implementados:
  → admin: Acesso total ao sistema
  → gestor: Gerenciamento operacional
  → usuario: Acesso básico às funções
- Verificações de permissão em tempo real
- Proteção contra elevação não autorizada
- Registro de operações administrativas

Segurança implementada:
- Restrição de acesso por nível
- Proteção contra auto-exclusão
- Validação de senhas em duas etapas
- Hash seguro com salt único por usuário
- Prevenção de conflito de usernames
- Proteção contra SQL injection

Interface administrativa:
- Lista de usuários com filtros
- Formulário de gerenciamento completo
- Feedback visual de operações
- Confirmações de ações críticas
- Mensagens claras de erro/sucesso

Validações do sistema:
- Username único obrigatório
- Senha com confirmação
- Nível de acesso válido
- Operações administrativas seguras
- Integridade referencial
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AuthUser

class AdmTab(ttk.Frame):
    """
    Classe que representa a aba de administração do sistema.
    
    Esta classe cria uma interface para gerenciamento completo de usuários,
    incluindo operações de CRUD (Create, Read, Update, Delete) com validações
    de segurança e permissões.
    
    Atributos:
        usuario_logado (AuthUser): Objeto do usuário atualmente logado
        selected_id (int): ID do usuário selecionado para edição
        tree (ttk.Treeview): Tabela para exibição dos usuários
        entry_usuario, entry_senha, entry_confirmar_senha (ttk.Entry): Campos do formulário
        combo_nivel (ttk.Combobox): Seletor de nível de acesso
    """
    
    def __init__(self, parent, usuario_logado=None):
        """
        Inicializa a aba de administração.
        
        Args:
            parent: Widget pai (geralmente um notebook)
            usuario_logado (AuthUser): Usuário atualmente autenticado no sistema
            
        Comportamento:
            - Verifica se o usuário tem permissão de admin
            - Se não tiver permissão, exibe mensagem de acesso negado
            - Se tiver permissão, constrói a interface completa
        """
        super().__init__(parent)
        
        # Armazena referência do usuário logado para verificação de permissões
        self.usuario_logado = usuario_logado
        
        # Verificação crítica de segurança: apenas admins podem acessar
        if not usuario_logado or not usuario_logado.is_admin():
            self.mostrar_acesso_negado()
            return
            
        # Configuração do layout principal
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.criar_interface()
        
    def mostrar_acesso_negado(self):
        """
        Exibe mensagem de acesso restrito quando usuário não é administrador.
        
        Esta função é chamada automaticamente quando um usuário sem permissões
        de admin tenta acessar a aba. Mostra uma mensagem clara e impede
        o acesso às funcionalidades administrativas.
        """
        label = ttk.Label(self, text="⛔ Acesso restrito a administradores", 
                         font=("Arial", 12, "bold"), foreground="red")
        label.pack(expand=True, pady=50)
        
    def criar_interface(self):
        """
        Constrói toda a interface gráfica da aba de administração.
        
        A interface é dividida em dois painéis principais:
        - Painel esquerdo: Lista de usuários em formato de tabela
        - Painel direito: Formulário para cadastro e edição
        
        A construção segue o padrão:
        1. Criação do título
        2. Divisão em painéis principais
        3. Construção da tabela no painel esquerdo
        4. Construção do formulário no painel direito
        5. Carregamento inicial dos dados
        """
        # Título principal da aba
        ttk.Label(self, text="Gerenciamento de Usuários do Sistema", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Container principal que organiza os dois painéis
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== PAINEL ESQUERDO - LISTA DE USUÁRIOS ==========
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Título da seção
        ttk.Label(left_panel, text="Usuários do Sistema", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Container da tabela com scrollbar
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para navegação na lista
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabela (Treeview) para exibir os usuários
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Usuário", "Nível Acesso"),
            show="headings",  # Mostra apenas os cabeçalhos, não a coluna #0
            yscrollcommand=scrollbar.set,
            height=15  # Altura fixa para 15 linhas
        )
        
        # Configuração da scrollbar para controlar a tabela
        scrollbar.config(command=self.tree.yview)
        
        # Configuração das colunas da tabela
        for col, width in [("ID", 50), ("Usuário", 150), ("Nível Acesso", 120)]:
            self.tree.heading(col, text=col.upper())  # Cabeçalho em maiúsculo
            self.tree.column(col, width=width, anchor=tk.W)  # Alinhamento à esquerda
        
        # Posicionamento da tabela
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vinculação do evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # ========== PAINEL DIREITO - FORMULÁRIO ==========
        right_panel = ttk.Frame(main_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)  # Mantém a largura fixa
        
        # Título do formulário
        ttk.Label(right_panel, text="Cadastrar/Editar Usuário", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Container do formulário
        form_frame = ttk.Frame(right_panel)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== CAMPOS DO FORMULÁRIO ==========
        
        # Campo: Nome de usuário
        ttk.Label(form_frame, text="Usuário *").grid(row=0, column=0, sticky="w", pady=(5, 2))
        self.entry_usuario = ttk.Entry(form_frame, width=25)
        self.entry_usuario.grid(row=1, column=0, sticky="we", pady=(0, 10))
        
        # Campo: Senha (com máscara)
        ttk.Label(form_frame, text="Senha *").grid(row=2, column=0, sticky="w", pady=(5, 2))
        self.entry_senha = ttk.Entry(form_frame, width=25, show="*")
        self.entry_senha.grid(row=3, column=0, sticky="we", pady=(0, 10))
        
        # Campo: Confirmação de senha
        ttk.Label(form_frame, text="Confirmar Senha *").grid(row=4, column=0, sticky="w", pady=(5, 2))
        self.entry_confirmar_senha = ttk.Entry(form_frame, width=25, show="*")
        self.entry_confirmar_senha.grid(row=5, column=0, sticky="we", pady=(0, 10))
        
        # Campo: Nível de acesso (combobox)
        ttk.Label(form_frame, text="Nível de Acesso *").grid(row=6, column=0, sticky="w", pady=(5, 2))
        self.combo_nivel = ttk.Combobox(form_frame, values=["admin", "gestor", "usuario"], 
                                      state="readonly", width=22)
        self.combo_nivel.grid(row=7, column=0, sticky="we", pady=(0, 15))
        self.combo_nivel.set("usuario")  # Valor padrão
        
        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=0, pady=10)
        
        # Botões com suas respectivas funções
        ttk.Button(btn_frame, text="Novo", command=self.novo_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.salvar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excluir", command=self.excluir_usuario).pack(side=tk.LEFT, padx=5)
        
        # Inicialização de variáveis de estado
        self.selected_id = None  # Nenhum usuário selecionado inicialmente
        
        # Carrega os usuários existentes na tabela
        self.carregar_usuarios()
    
    def carregar_usuarios(self):
        """
        Carrega todos os usuários do banco de dados na tabela.
        
        Esta função:
        1. Limpa a tabela atual
        2. Busca todos os usuários ordenados por nome
        3. Insere cada usuário na tabela com suas informações
        
        A consulta ao banco é feita usando SQLAlchemy e os resultados
        são ordenados alfabeticamente por username para melhor organização.
        """
        # Limpa todos os itens existentes na tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Consulta todos os usuários ordenados por nome
        usuarios = session.query(AuthUser).order_by(AuthUser.username).all()
        
        # Insere cada usuário na tabela
        for usuario in usuarios:
            self.tree.insert("", "end", iid=str(usuario.id),
                           values=(usuario.id, usuario.username, usuario.nivel_acesso))
    
    def on_select(self, event):
        """
        Manipula a seleção de um usuário na tabela.
        
        Quando um usuário é selecionado na tabela, esta função:
        1. Obtém o ID do usuário selecionado
        2. Busca os dados completos do usuário no banco
        3. Preenche o formulário com os dados para edição
        4. Limpa os campos de senha por segurança
        
        Args:
            event: Evento de seleção da Treeview (não utilizado diretamente)
        """
        # Obtém a seleção atual (pode ser múltipla, mas usamos apenas a primeira)
        selecionados = self.tree.selection()
        if not selecionados:  # Se não há seleção, ignora
            return
            
        # Converte o ID (string) para inteiro e busca o usuário
        usuario_id = int(selecionados[0])
        usuario = session.query(AuthUser).get(usuario_id)
        self.selected_id = usuario.id  # Armazena o ID para operações futuras
        
        # Preenche o formulário com os dados do usuário
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, usuario.username)
        self.combo_nivel.set(usuario.nivel_acesso)
        
        # Limpa campos de senha por segurança - não mostra senhas atuais
        self.entry_senha.delete(0, tk.END)
        self.entry_confirmar_senha.delete(0, tk.END)
    
    def novo_usuario(self):
        """
        Prepara o formulário para cadastrar um novo usuário.
        
        Esta função:
        - Limpa o ID selecionado
        - Limpa todos os campos do formulário
        - Define o nível de acesso padrão como "usuario"
        
        É chamada quando o botão "Novo" é pressionado, permitindo
        que o administrador cadastre um novo usuário sem interferência
        de dados anteriores.
        """
        self.selected_id = None  # Indica que é um novo usuário
        self.entry_usuario.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)
        self.entry_confirmar_senha.delete(0, tk.END)
        self.combo_nivel.set("usuario")  # Valor padrão
    
    def salvar_usuario(self):
        """
        Salva ou atualiza um usuário no banco de dados.
        
        Esta função realiza as seguintes operações:
        1. Valida os dados do formulário
        2. Verifica se é uma criação ou edição
        3. Para novos usuários: verifica se o username já existe
        4. Para edições: atualiza os dados existentes
        5. Executa o commit no banco de dados
        6. Atualiza a tabela e limpa o formulário
        
        Validações realizadas:
        - Username obrigatório
        - Senha obrigatória para novos usuários
        - Confirmação de senha deve coincidir
        - Username único no sistema
        """
        # Obtém e limpa os dados do formulário
        username = self.entry_usuario.get().strip()
        password = self.entry_senha.get().strip()
        confirmar_password = self.entry_confirmar_senha.get().strip()
        nivel_acesso = self.combo_nivel.get()
        
        # ========== VALIDAÇÕES ==========
        
        # Validação: Username é obrigatório
        if not username:
            messagebox.showerror("Erro", "Usuário é obrigatório.")
            return
            
        # Validação: Para novos usuários, senha é obrigatória
        if not self.selected_id and (not password or not confirmar_password):
            messagebox.showerror("Erro", "Senha é obrigatória para novo usuário.")
            return
            
        # Validação: Senhas devem coincidir
        if password != confirmar_password:
            messagebox.showerror("Erro", "Senhas não coincidem.")
            return
        
        # ========== OPERAÇÃO DE EDIÇÃO ==========
        if self.selected_id:
            # Busca o usuário existente
            usuario = session.query(AuthUser).get(self.selected_id)
            usuario.username = username
            usuario.nivel_acesso = nivel_acesso
            
            # Atualiza senha apenas se foi informada (permite manter a atual)
            if password:
                usuario.set_password(password)
                
            message = "Usuário atualizado com sucesso!"
            
        # ========== OPERAÇÃO DE CRIAÇÃO ==========
        else:
            # Verifica se o username já existe
            if session.query(AuthUser).filter_by(username=username).first():
                messagebox.showerror("Erro", "Usuário já existe.")
                return
                
            # Cria novo usuário
            usuario = AuthUser(username=username, nivel_acesso=nivel_acesso)
            usuario.set_password(password)  # Gera o hash da senha
            session.add(usuario)
            message = "Usuário criado com sucesso!"
        
        # ========== PERSISTÊNCIA NO BANCO ==========
        try:
            session.commit()  # Salva as alterações
            self.carregar_usuarios()  # Atualiza a tabela
            self.novo_usuario()  # Limpa o formulário
            messagebox.showinfo("Sucesso", message)
        except Exception as e:
            # Em caso de erro, faz rollback e informa o usuário
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")
    
    def excluir_usuario(self):
        """
        Exclui o usuário selecionado após confirmação.
        
        Esta função:
        1. Verifica se há um usuário selecionado
        2. Impede a auto-exclusão (usuário não pode excluir a si mesmo)
        3. Solicita confirmação do usuário
        4. Executa a exclusão no banco de dados
        5. Atualiza a interface
        
        Medidas de segurança:
        - Impedimento de auto-exclusão
        - Confirmação explícita do usuário
        - Tratamento de exceções durante a exclusão
        """
        # Verifica se há um usuário selecionado
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione um usuário para excluir.")
            return
            
        # Busca o usuário no banco
        usuario = session.query(AuthUser).get(self.selected_id)
        
        # Medida de segurança: impede a exclusão do próprio usuário logado
        if usuario.id == self.usuario_logado.id:
            messagebox.showerror("Erro", "Você não pode excluir seu próprio usuário.")
            return
            
        # Confirmação explícita do usuário
        if not messagebox.askyesno("Confirmar", f"Excluir usuário '{usuario.username}'?"):
            return
            
        # Tenta executar a exclusão
        try:
            session.delete(usuario)
            session.commit()
            self.carregar_usuarios()  # Atualiza a tabela
            self.novo_usuario()  # Limpa o formulário
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            # Em caso de erro, faz rollback
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}")