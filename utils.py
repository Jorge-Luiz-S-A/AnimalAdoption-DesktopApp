# utils.py
from datetime import datetime, date
from typing import Optional

# Constants
STATUSES = ["available", "in_process", "adopted"]
ADOPTION_STEPS = ["questionnaire", "screening", "visit", "docs", "approved", "finalized", "declined"]
SIZES = ["pequeno", "médio", "grande", ""]
GENDERS = ["macho", "fêmea", ""]

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
    # Tenta ISO 8601: YYYY-MM-DDTHH:MM
    try:
        return datetime.fromisoformat(s)
    except Exception:
        # fallback: "YYYY-MM-DD HH:MM"
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
