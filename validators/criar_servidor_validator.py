from cerberus import Validator
from datetime import time, datetime

def validate_time(field, value, error):
    try:
        if len(value) == 7: 
            value = f"0{value}" 
        time.fromisoformat(value) 
    except ValueError:
        error(field, "Formato de horário inválido. Use H:MM:SS ou HH:MM:SS")

def validate_date(field, value, error):
    try:
        datetime.fromisoformat(value)
    except ValueError:
        error(field, "Formato de data inválido. Use YYYY-MM-DD")

schema = {
    "setor": {
        "type": "string", 
        "required": True,
         "minlength": 3
    },
    "nome": {
        "type": "string", 
        "required": True, 
        "minlength": 3
    },
    "matricula": {
        "type": "string", 
        "required": True, 
        "minlength": 3
    },
    "cargo": {
        "type": "string", 
        "required": True, 
        "minlength": 3
    },
    "funcao": {
        "type": "string", 
        "required": False
    },
    "horario": {
        "type": "string", 
        "required": True
    },
    "entrada": {
        "type": "string", 
        "required": True,
        "check_with": validate_time
    },
    "saida": {
        "type": "string", 
        "required": True,
        "check_with": validate_time
    },
    "ferias_inicio": {
        "type": "string", 
        "required": False,
        "check_with": validate_date
    },
    "ferias_termino": {
        "type": "string", 
        "required": False,
        "check_with": validate_date
    }
}

validator = Validator(schema)
