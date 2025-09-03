"""
Utilitários do Sistema
---------------------
Funções auxiliares para formatação, parsing e validação de dados.
"""

from datetime import datetime, date
from typing import Optional

# Constantes para valores predefinidos
STATUSES = ["", "Disponível", "Em processo", "Adotado", "Indisponível"]
ADOPTION_STEPS = ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado", "Finalizado", "Recusado"]
SIZES = ["", "Pequeno", "Médio", "Grande"]
GENDERS = ["", "Macho", "Fêmea"]

def parse_bool(value: str) -> bool:
    """
    Converte uma string para booleano.
    
    Args:
        value (str): Valor a ser convertido
        
    Returns:
        bool: True se a string representar um valor verdadeiro, False caso contrário
    """
    return str(value).strip().lower() in ("1", "true", "t", "yes", "y", "sim")

def parse_int(s: str, default: int = 0) -> int:
    """
    Converte uma string para inteiro, retornando um valor padrão em caso de erro.
    
    Args:
        s (str): String a ser convertida
        default (int): Valor padrão a ser retornado em caso de erro
        
    Returns:
        int: Valor inteiro convertido ou valor padrão
    """
    try:
        return int(s)
    except Exception:
        return default

def parse_date_str(s: str) -> Optional[date]:
    """
    Converte uma string no formato ISO para objeto date.
    
    Args:
        s (str): String no formato YYYY-MM-DD
        
    Returns:
        Optional[date]: Objeto date ou None se a conversão falhar
    """
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None

def parse_dt_str(s: str) -> Optional[datetime]:
    """
    Converte uma string para objeto datetime.
    
    Args:
        s (str): String em formato ISO ou YYYY-MM-DD HH:MM
        
    Returns:
        Optional[datetime]: Objeto datetime ou None se a conversão falhar
    """
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M")
        except Exception:
            return None

def yes_no(v: Optional[bool]) -> str:
    """
    Converte um booleano para representação em português.
    
    Args:
        v (Optional[bool]): Valor booleano a ser convertido
        
    Returns:
        str: "Sim" para True, "Não" para False, "-" para None
    """
    if v is True:
        return "Sim"
    if v is False:
        return "Não"
    return "-"

def combobox_set(cb, value: str):
    """
    Define o valor de um Combobox se o valor estiver na lista de opções.
    
    Args:
        cb: Widget Combobox
        value (str): Valor a ser definido
    """
    if value in cb["values"]:
        cb.set(value)
    else:
        cb.set("")