"""
Módulo de Utilitários - Funções Auxiliares do Sistema
-----------------------------------------------------
Este módulo implementa um conjunto de ferramentas, utilitários e
constantes que são utilizados em todo o sistema, garantindo consistência
e reusabilidade.

1. Constantes do Sistema:
   - Status de animais e processos
   - Etapas padronizadas de adoção
   - Características físicas (porte, gênero)
   - Valores predefinidos para seleção

2. Funções de Conversão:
   - Parsing seguro de tipos primitivos
   - Tratamento robusto de erros
   - Valores padrão configuráveis
   - Normalização de formatos

3. Manipulação de Datas:
   - Conversão de strings para date/datetime
   - Múltiplos formatos suportados
   - Validação de datas
   - Formatação padronizada

4. Formatação de Valores:
   - Conversão para exibição amigável
   - Internacionalização (pt-BR)
   - Tratamento de valores nulos
   - Consistência visual

5. Validações Utilitárias:
   - Verificação de tipos
   - Normalização de strings
   - Validação de formatos
   - Tratamento de exceções

6. Recursos Adicionais:
   - Funções de UI (combobox)
   - Helpers para logging
   - Formatadores especializados
   - Conversores customizados
"""

from datetime import datetime, date
from typing import Optional

# ========== CONSTANTES PREDEFINIDAS ==========

# Status disponíveis para animais
STATUSES = ["", "Disponível", "Em processo", "Adotado", "Indisponível"]

# Etapas do processo de adoção
ADOPTION_STEPS = ["", "Questionário", "Documentos", "Visita", "Aprovado", "Finalizado", "Recusado"]

# Portes disponíveis para animais
SIZES = ["", "Pequeno", "Médio", "Grande"]

# Gêneros disponíveis para animais
GENDERS = ["", "Macho", "Fêmea"]

# ========== FUNÇÕES DE PARSING ==========

def parse_bool(value: str) -> bool:
    """
    Converte uma string para booleano de forma robusta.
    
    Args:
        value (str): Valor a ser convertido. Aceita múltiplos formatos.
        
    Returns:
        bool: True para valores que representam verdadeiro, False caso contrário.
        
    Exemplos:
        parse_bool("1") → True
        parse_bool("true") → True
        parse_bool("sim") → True
        parse_bool("0") → False
        parse_bool("não") → False
    """
    return str(value).strip().lower() in ("1", "true", "t", "yes", "y", "sim", "verdadeiro")

def parse_int(s: str, default: int = 0) -> int:
    """
    Converte uma string para inteiro com valor padrão em caso de erro.
    
    Args:
        s (str): String a ser convertida
        default (int): Valor a retornar se a conversão falhar
        
    Returns:
        int: Valor inteiro convertido ou valor padrão
        
    Exemplos:
        parse_int("123") → 123
        parse_int("abc") → 0
        parse_int("", 10) → 10
    """
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

def parse_date_str(s: str) -> Optional[date]:
    """
    Converte uma string no formato ISO para objeto date.
    
    Args:
        s (str): String no formato YYYY-MM-DD
        
    Returns:
        Optional[date]: Objeto date ou None se a conversão falhar
        
    Exemplos:
        parse_date_str("2023-12-25") → datetime.date(2023, 12, 25)
        parse_date_str("invalid") → None
    """
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None

def parse_dt_str(s: str) -> Optional[datetime]:
    """
    Converte uma string para objeto datetime com múltiplos formatos.
    
    Args:
        s (str): String em formato ISO ou YYYY-MM-DD HH:MM
        
    Returns:
        Optional[datetime]: Objeto datetime ou None se a conversão falhar
        
    Exemplos:
        parse_dt_str("2023-12-25 14:30") → datetime(2023, 12, 25, 14, 30)
        parse_dt_str("2023-12-25T14:30:00") → datetime(2023, 12, 25, 14, 30)
        parse_dt_str("invalid") → None
    """
    if not s:
        return None
    try:
        # Tenta formato ISO primeiro
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        try:
            # Tenta formato alternativo
            return datetime.strptime(s, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return None

# ========== FUNÇÕES DE FORMATAÇÃO ==========

def yes_no(v: Optional[bool]) -> str:
    """
    Converte um booleano para representação em português.
    
    Args:
        v (Optional[bool]): Valor booleano a ser convertido
        
    Returns:
        str: "Sim" para True, "Não" para False, "-" para None
        
    Exemplos:
        yes_no(True) → "Sim"
        yes_no(False) → "Não"
        yes_no(None) → "-"
    """
    if v is True:
        return "Sim"
    if v is False:
        return "Não"
    return "-"

def combobox_set(cb, value: str):
    """
    Define o valor de um Combobox apenas se o valor estiver na lista de opções.
    
    Esta função previte erros ao tentar definir valores inválidos em comboboxes.
    
    Args:
        cb: Widget Combobox do tkinter
        value (str): Valor a ser definido
        
    Comportamento:
        - Se value está em cb["values"], define o valor
        - Caso contrário, limpa o combobox
    """
    if value in cb["values"]:
        cb.set(value)
    else:
        cb.set("")
