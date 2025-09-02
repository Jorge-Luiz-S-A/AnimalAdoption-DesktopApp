# utils.py
from datetime import datetime, date
from typing import Optional

STATUSES = ["","Disponível", "Em processo", "Adotado", "Indisponível"]
ADOPTION_STEPS = ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado", "Finalizado", "Recusado"]
SIZES = ["", "Pequeno", "Médio", "Grande"]
GENDERS = ["", "Macho", "Fêmea"]

def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "t", "yes", "y", "sim")

def parse_int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except Exception:
        return default

def parse_date_str(s: str) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None

def parse_dt_str(s: str) -> Optional[datetime]:
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
    if v is True:
        return "Sim"
    if v is False:
        return "Não"
    return "-"

def combobox_set(cb, value: str):
    if value in cb["values"]:
        cb.set(value)
    else:
        cb.set("")
