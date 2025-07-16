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
    'setor': {'type': 'string', 'required': True},
    'nome': {'type': 'string', 'required': True},
    'matricula': {'type': 'string', 'required': True},
    'cargo': {'type': 'string', 'required': True},
    'horario': {'type': 'string', 'required': True},
    'entrada': {'type': 'string', 'required': True},
    'saida': {'type': 'string', 'required': True},
    'data_nascimento': {'type': 'string', 'required': True},
    'sexo': {'type': 'string', 'required': True},
    'estado_civil': {'type': 'string', 'required': True},
    'naturalidade': {'type': 'string', 'required': True},
    'nacionalidade': {'type': 'string', 'required': True},
    'identidade': {'type': 'string', 'required': True},
    'titulo_eleitor': {'type': 'string', 'required': True},
    'cpf': {'type': 'string', 'required': True},
    'pis': {'type': 'string', 'required': True},
    'data_admissao': {'type': 'string', 'required': True},
    
    # --- NOVOS CAMPOS ADICIONADOS AO SCHEMA ---
    'endereco': {'type': 'string', 'required': False, 'nullable': True},
    'nome_pai': {'type': 'string', 'required': False, 'nullable': True},
    'nome_mae': {'type': 'string', 'required': False, 'nullable': True},
    'servico_militar': {'type': 'string', 'required': False, 'nullable': True},
    'carteira_profissional': {'type': 'string', 'required': False, 'nullable': True},
    'data_posse': {'type': 'string', 'required': False, 'nullable': True, 'nullable': True},
}


validator = Validator(schema)
