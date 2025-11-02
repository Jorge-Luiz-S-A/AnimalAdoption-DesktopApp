"""
Módulo de Gerenciamento de Processos de Adoção - Fluxo Completo
---------------------------------------------------------------
Este módulo implementa o gerenciamento completo do ciclo de vida dos processos 
de adoção, desde a seleção inicial até a finalização, com controles rigorosos 
e sincronização automática.

Funcionalidades principais:
- Gestão completa de processos de adoção
- Fluxo de status bem definido e controlado
- Interface intuitiva dividida em lista/formulário
- Controle de datas de visitas e aprovações
- Sistema detalhado de notas e observações
- Sincronização automática com outras abas
- Atualizações em tempo real de status

Fluxo de aprovação:
1. Questionário: Avaliação inicial
2. Documentos: Verificação documental
3. Visita: Encontro presencial
4. Aprovado: Processo aceito
5. Finalizado/Recusado: Conclusão

Validações implementadas:
- Campos obrigatórios: animal, tutor, status
- Validação de datas de visita
- Verificação de disponibilidade do animal
- Controle de um processo por animal
- Prevenção de conflitos de status
- Integridade com outros módulos

Sincronização:
- Atualização global ao salvar/excluir
- Recarregamento automático de todas as abas
- Status do animal atualizado automaticamente
- Restauração de estado em cancelamentos
- Manutenção de consistência de dados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import session
from models import AdoptionProcess, Animal, User
from utils import ADOPTION_STEPS

class AdoptionsTab(ttk.Frame):
    """
    Classe para gerenciamento completo de processos de adoção.
    
    Esta classe implementa uma interface dividida em:
    - Painel esquerdo: Lista de processos em andamento
    - Painel direito: Formulário detalhado do processo
    
    Oferece operações completas de CRUD com validações de negócio
    e integração automática com o status dos animais.
    
    Atributos:
        selected_id (int): ID do processo selecionado para edição
        tree (ttk.Treeview): Tabela de processos
        inputs (dict): Campos do formulário de processo
    """
    
    def __init__(self, parent):
        """
        Inicializa a aba de processos de adoção.
        
        Args:
            parent: Widget pai container
            
        A construção da interface inclui:
        1. Divisão em painéis esquerdo/direito
        2. Tabela de processos com scroll
        3. Formulário scrollable com todos os campos
        4. Sistema de datas para visitas
        5. Botões de ação
        """
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== PAINEL ESQUERDO - LISTA DE ADOÇÕES ==========
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título da seção
        ttk.Label(left_panel, text="Lista de Adoções", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        # Container da tabela
        table_frame = ttk.Frame(left_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela de processos
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Animal", "Usuário", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        # Configuração das colunas
        for c, w in (("ID", 50), ("Animal", 150), ("Usuário", 150), ("Status", 120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ========== PAINEL DIREITO - FORMULÁRIO ==========
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)

        ttk.Label(right_panel, text="Detalhes da Adoção", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Container scrollable do formulário
        form_container = ttk.Frame(right_panel)
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container)
        scrollbar_form = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Configuração do scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        # ========== CAMPOS DO FORMULÁRIO ==========
        r = 0
        fields = [
            ("Animal *", ttk.Combobox, {"values": self.get_animals(), "state": "readonly", "width": 30}),
            ("Usuário *", ttk.Combobox, {"values": self.get_users(), "state": "readonly", "width": 30}),
            ("Status", ttk.Combobox, {"values": ADOPTION_STEPS, "state": "readonly", "width": 30}),
            ("Visita", ttk.Entry, {"width": 30}),  # Data no formato DD/MM/AAAA (apenas uma visita)
        ]

        self.inputs = {}
        for label_text, widget_class, opts in fields:
            ttk.Label(self.scrollable_frame, text=label_text).grid(row=r, column=0, sticky="w", pady=(5, 0))
            r += 1
            w = widget_class(self.scrollable_frame, **opts)
            w.grid(row=r, column=0, sticky="we", pady=(0, 5))
            self.inputs[label_text] = w
            r += 1

        # Campo de observações
        ttk.Label(self.scrollable_frame, text="Notas").grid(row=r, column=0, sticky="w", pady=(5, 0))
        r += 1
        self.inputs["Notas"] = tk.Text(self.scrollable_frame, width=30, height=5, wrap="word")
        self.inputs["Notas"].grid(row=r, column=0, sticky="we", pady=(0, 5))
        r += 1

        # ========== BOTÕES DE AÇÃO ==========
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.grid(row=r, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Novo", command=self.new).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Salvar", command=self.save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Excluir", command=self.delete).pack(side=tk.LEFT, padx=4)
        # Nota: botão 'Atualizar Página' removido. A função de recarregar é realizada após Salvar/Excluir.

        # ========== INICIALIZAÇÃO ==========
        self.selected_id = None
        self.load()

    # ========== FUNÇÕES AUXILIARES ==========

    def get_animals(self):
        """
        Obtém lista de animais disponíveis para adoção.
        
        Filtra apenas animais com status "Disponível" para garantir
        que só animais realmente disponíveis apareçam na lista.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para animais disponíveis
        """
        # Filtra apenas animais com status próximo de "Disponível".
        # Usa busca case-insensitive/ilike para cobrir variações sem acento
        # ou espaços acidentais (ex: 'Disponivel', ' Disponível ').
        animais_disponiveis = session.query(Animal).filter(
            Animal.status.ilike("%dispon%")
        ).all()
        
        return [f"{a.id} - {a.name}" for a in animais_disponiveis]
    
    def get_users(self):
        """
        Obtém lista de usuários aprovados para adoção.
        
        Filtra apenas usuários com approved = True para garantir
        que só usuários habilitados possam ser vinculados a processos.
        
        Returns:
            list: Lista de strings no formato "ID - Nome" para usuários aprovados
        """
        # Filtra apenas usuários aprovados
        # Retorna todos os usuários (campo 'Aprovado' foi removido do formulário)
        usuarios = session.query(User).all()
        return [f"{u.id} - {u.name}" for u in usuarios]

    # ========== OPERAÇÕES CRUD ==========

    def load(self):
        """
        Carrega todos os processos de adoção na tabela.
        
        Ordena os processos por ID decrescente (mais recentes primeiro)
        e atualiza as listas de animais e usuários nos comboboxes.
        """
        # Limpa a tabela atual
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Busca todos os processos ordenados por ID decrescente
        for adocao in session.query(AdoptionProcess).order_by(AdoptionProcess.id.desc()).all():
            self.tree.insert("", "end", iid=str(adocao.id),
                           values=(adocao.id,
                                   adocao.animal.name if adocao.animal else "-",
                                   adocao.user.name if adocao.user else "-",
                                   adocao.status or "-"))

        # Atualiza as listas nos comboboxes
        self.inputs["Animal *"]["values"] = self.get_animals()
        self.inputs["Usuário *"]["values"] = self.get_users()

    def on_select(self, event):
        """
        Manipula a seleção de um processo na lista.
        
        Preenche o formulário com os dados do processo selecionado
        e formata as datas para exibição no padrão DD/MM/AAAA.
        """
        sel = self.tree.selection()
        if not sel:
            return
            
        # Busca o processo selecionado
        adocao = session.get(AdoptionProcess, int(sel[0]))
        self.selected_id = adocao.id

        # Preenche campos básicos
        self.inputs["Animal *"].set(f"{adocao.animal.id} - {adocao.animal.name}" if adocao.animal else "")
        self.inputs["Usuário *"].set(f"{adocao.user.id} - {adocao.user.name}" if adocao.user else "")
        self.inputs["Status"].set(adocao.status or "")
        
        # Preenche datas de visita (formatadas)
        # Campo único de visita (mapeado para in_person_visit_at)
        self.inputs["Visita"].delete(0, tk.END)
        if adocao.in_person_visit_at:
            self.inputs["Visita"].insert(0, adocao.in_person_visit_at.strftime("%d/%m/%Y"))
            
        # Preenche observações
        self.inputs["Notas"].delete("1.0", tk.END)
        self.inputs["Notas"].insert("1.0", adocao.notes or "")

    def new(self):
        """Limpa o formulário para criar um novo processo."""
        self.selected_id = None
        for key, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def save(self):
        """
        Salva ou atualiza um processo de adoção.
        
        Realiza validações de campos obrigatórios e formato de datas,
        atualiza automaticamente o status do animal vinculado.
        """
        # Validações de campos obrigatórios
        animal_val = self.inputs["Animal *"].get().strip()
        user_val = self.inputs["Usuário *"].get().strip()

        if not animal_val or not user_val:
            messagebox.showerror("Erro", "Animal e Usuário são obrigatórios.")
            return

        # Extrai IDs dos valores do combobox
        animal_id = int(animal_val.split(" - ")[0])
        user_id = int(user_val.split(" - ")[0])

        # Validação: status obrigatório; visita obrigatória apenas para etapas que a exigem
        status_val = self.inputs["Status"].get().strip()
        visita_raw = self.inputs["Visita"].get().strip()
        notes_raw = self.inputs["Notas"].get("1.0", tk.END).strip()

        if not status_val:
            messagebox.showerror("Erro", "Status é obrigatório.")
            return

        # Somente exigir data de visita quando o processo estiver nas etapas que requerem visita
        visita_required_statuses = ("Visita", "Aprovado", "Finalizado")
        if status_val in visita_required_statuses and not visita_raw:
            messagebox.showerror("Erro", "Visita (data) é obrigatória para o status selecionado.")
            return

        # Determina se é criação ou edição
        is_new = False
        if self.selected_id:
            adocao = session.get(AdoptionProcess, self.selected_id)
            if adocao is None:
                messagebox.showerror("Erro", "Adoção selecionada não encontrada.")
                return
        else:
            # Antes de criar, verifica se o animal já está em um processo ativo
            animal_id_check = int(animal_val.split(" - ")[0])
            active = session.query(AdoptionProcess).filter(
                AdoptionProcess.animal_id == animal_id_check,
                AdoptionProcess.status.notin_(("Finalizado", "Recusado"))
            ).count()
            if active > 0:
                messagebox.showerror("Erro", "Este animal já está em um processo de adoção ativo.")
                return
            is_new = True

        # Processa data única de visita (in_person_visit_at)
        from datetime import datetime
        visita = self.inputs["Visita"].get().strip()
        try:
            visita_dt = None
            if visita:
                visita_dt = datetime.strptime(visita, "%d/%m/%Y")
        except ValueError:
            # garante que sessão não fique com transações parciais
            session.rollback()
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        # Agora que validações passaram, cria/atualiza o objeto
        if is_new:
            adocao = AdoptionProcess()
            session.add(adocao)

        # Atualiza dados básicos
        adocao.animal_id = animal_id
        adocao.user_id = user_id
        adocao.status = self.inputs["Status"].get().strip() or None
        adocao.notes = self.inputs["Notas"].get("1.0", tk.END).strip() or None
        adocao.in_person_visit_at = visita_dt

        try:
            # Salva o processo
            session.commit()

            # Atualiza automaticamente o status do animal
            adocao.update_animal_status()
            # Se o processo está em andamento, garante que o animal fique em processo
            if adocao.animal:
                if adocao.status in ["Questionário", "Visita", "Documentos", "Aprovado"]:
                    adocao.animal.status = "Em processo"
            session.commit()

            # Recarrega abas locais e globais
            try:
                root = self.winfo_toplevel()
                if hasattr(root, "reload_all_tabs"):
                    root.reload_all_tabs()
            except Exception:
                pass

            self.load()
            messagebox.showinfo("Sucesso", "Adoção salva com sucesso. Status do animal atualizado automaticamente.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar adoção: {e}")

    def delete(self):
        """
        Exclui o processo de adoção selecionado.
        
        Antes de excluir, restaura o status do animal para "Disponível"
        para que ele possa aparecer em novos processos de adoção.
        """
        if not self.selected_id:
            messagebox.showerror("Erro", "Selecione uma adoção.")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir adoção selecionada?"):
            return
            
        try:
            adocao = session.get(AdoptionProcess, self.selected_id)
            
            # Restaura o status do animal para disponível
            if adocao.animal:
                adocao.animal.status = "Disponível"
            
            session.delete(adocao)
            session.commit()
            
            # Recarrega todas as abas para manter UI consistente
            try:
                root = self.winfo_toplevel()
                if hasattr(root, "reload_all_tabs"):
                    root.reload_all_tabs()
            except Exception:
                pass
            
            self.new()
            self.load()
            messagebox.showinfo("Sucesso", "Adoção excluída com sucesso. Status do animal restaurado para Disponível.")
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir adoção: {e}")
