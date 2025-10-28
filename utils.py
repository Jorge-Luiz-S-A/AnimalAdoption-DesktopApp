# utils.py (expandido)
"""
Utilitários completos do sistema
"""
from datetime import datetime, date
from typing import Optional

# Constantes
STATUSES = ["", "Disponível", "Em processo", "Adotado", "Indisponível"]
ADOPTION_STEPS = ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado", "Finalizado", "Recusado"]
SIZES = ["", "Pequeno", "Médio", "Grande"]
GENDERS = ["", "Macho", "Fêmea"]

def parse_bool(value: str) -> bool:
    """Converte string para booleano"""
    return str(value).strip().lower() in ("1", "true", "t", "yes", "y", "sim", "verdadeiro")

def parse_int(s: str, default: int = 0) -> int:
    """Converte para inteiro com valor padrão"""
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

def parse_date_str(s: str) -> Optional[date]:
    """Converte string para data"""
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None

def parse_dt_str(s: str) -> Optional[datetime]:
    """Converte string para datetime"""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return None

def yes_no(v: Optional[bool]) -> str:
    """Formata booleano para Sim/Não"""
    if v is True:
        return "Sim"
    if v is False:
        return "Não"
    return "-"

def combobox_set(cb, value: str):
    """Define valor do combobox apenas se existir na lista"""
    if value in cb["values"]:
        cb.set(value)
    else:
        cb.set("")
