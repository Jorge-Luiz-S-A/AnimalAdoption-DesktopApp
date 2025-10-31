"""
Classe Base para Abas do Sistema - Framework Comum
--------------------------------------------------
Esta classe fornece uma base sólida para todas as abas do sistema, implementando
funcionalidades comuns, estilos padronizados e métodos utilitários que são
reutilizados em toda a aplicação.

Funcionalidades fornecidas:
- Configuração centralizada de estilos visuais
- Métodos padronizados para exibição de mensagens ao usuário
- Sistema de criação de campos de formulário com labels
- Tratamento consistente de erros e informações

Padrões de design implementados:
- DRY (Don't Repeat Yourself): Código comum centralizado
- Consistency: Interface visual padronizada
- Maintainability: Facilidade de manutenção e extensão
"""

import tkinter as tk
from tkinter import ttk, messagebox

class BaseTab(ttk.Frame):
    """
    Classe base abstrata para todas as abas do sistema de gerenciamento.
    
    Esta classe serve como um template para criação de novas abas, fornecendo
    uma estrutura consistente e funcionalidades comuns. Todas as abas do sistema
    herdam desta classe para garantir uniformidade no comportamento e aparência.
    
    Atributos:
        style (ttk.Style): Objeto para gerenciamento de estilos da interface
        parent (widget): Referência ao widget pai container
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba base com configurações comuns.
        
        Args:
            parent: Widget pai onde a aba será inserida, geralmente um Notebook
                   ou Frame container principal.
                   
        Configurações realizadas:
        - Herda da classe ttk.Frame para compatibilidade temática
        - Inicializa o sistema de estilos do ttk
        - Define estilos padrão para labels e botões
        - Integra com tema sv_ttk para aparência moderna
        """
        super().__init__(parent)
        self.style = ttk.Style()
        
        # Configuração de estilos visuais padronizados
        # Compatíveis com o tema sv_ttk para consistência visual
        self.style.configure("Header.TLabel", 
                           font=("Segoe UI", 10, "bold"),
                           foreground="#2c3e50")  # Azul escuro elegante
        
        self.style.configure("Required.TLabel", 
                           foreground="#e74c3c",  # Vermelho para indicar obrigatoriedade
                           font=("Segoe UI", 9, "bold"))
        
        self.style.configure("Success.TButton",
                           foreground="#27ae60")  # Verde para ações positivas

    def info(self, msg: str):
        """
        Exibe uma mensagem de informação para o usuário.
        
        Este método fornece uma interface padronizada para mostrar informações
        ao usuário, usando o sistema de messagebox do tkinter com estilo
        consistente em toda a aplicação.
        
        Args:
            msg (str): Mensagem de texto a ser exibida ao usuário.
                      Deve ser clara, concisa e informativa.
                      
        Exemplo de uso:
            self.info("Animal cadastrado com sucesso!")
        """
        messagebox.showinfo("Informação", msg)

    def error(self, msg: str):
        """
        Exibe uma mensagem de erro para o usuário.
        
        Método padronizado para comunicação de erros ou situações problemáticas
        ao usuário. Usa o estilo de erro do sistema operacional para máxima
        clareza e reconhecimento.
        
        Args:
            msg (str): Mensagem de erro descrevendo o problema encontrado.
                      Deve ser específica e orientar sobre a solução.
                      
        Exemplo de uso:
            self.error("Nome do animal é obrigatório!")
        """
        messagebox.showerror("Erro", msg)

    def create_form_field(self, parent, label, row, required=False, tooltip=None):
        """
        Cria um campo de formulário padronizado com label.
        
        Este método implementa um padrão de criação de campos de formulário
        que garante consistência visual e comportamental em toda a aplicação.
        É especialmente útil para forms com múltiplos campos.
        
        Args:
            parent: Widget pai onde o campo será criado
            label (str): Texto descritivo do campo
            row (int): Linha do grid onde o campo será posicionado
            required (bool): Se True, marca o campo como obrigatório
            tooltip (str, optional): Texto de ajuda flutuante
            
        Returns:
            int: Próxima linha disponível no grid (row + 1)
            
        Exemplo de uso:
            next_row = self.create_form_field(form, "Nome *", 0, True)
            entry_nome = ttk.Entry(form)
            entry_nome.grid(row=next_row, column=0, sticky="we")
        """
        # Cria o label do campo
        label_widget = ttk.Label(parent, text=label)
        
        # Aplica estilo de campo obrigatório se necessário
        if required:
            label_widget.configure(style="Required.TLabel")
        
        # Posiciona o label no grid
        label_widget.grid(row=row, column=0, sticky="w", pady=(5, 2))
        
        # Retorna a próxima linha disponível para o widget de entrada
        return row + 1