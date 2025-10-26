# utils.py
"""
Funções utilitárias para o sistema
"""
from datetime import datetime

# Constantes para comboboxes
STATUSES = ["Disponível", "Em processo", "Adotado", "Indisponível"]
ADOPTION_STEPS = ["Questionário", "Triagem", "Visita", "Documentos", "Aprovado", "Finalizado"]
SIZES = ["Pequeno", "Médio", "Grande"]
GENDERS = ["Macho", "Fêmea"]

def parse_int(valor, padrao=0):
    """Converte para inteiro com valor padrão"""
    try:
        return int(valor)
    except:
        return padrao

def parse_bool(valor):
    """Converte para booleano"""
    return str(valor).lower() in ("1", "true", "sim", "yes")

def yes_no(valor):
    """Formata booleano para Sim/Não"""
    return "Sim" if valor else "Não"