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

schema_estagiario = {  # Nome alterado para evitar conflito
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
    # REMOVA 'matricula' aqui!
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
    "entrada": {  # Campo usado no código: body.get('entrada')
        "type": "string", 
        "required": True,
        "check_with": validate_time
    },
    "saida": {  # Campo usado no código: body.get('saida')
        "type": "string", 
        "required": True,
        "check_with": validate_time
    },
    # Ajuste os nomes para bater com o código:
    "feriasinicio": {  # Antes era 'ferias_inicio'
        "type": "string", 
        "required": False,
        "check_with": validate_date
    },
    "feriasfinal": {  # Antes era 'ferias_termino'
        "type": "string", 
        "required": False,
        "check_with": validate_date
    }
}

validator_estagiario = Validator(schema_estagiario)  # Nome do validator alterado
