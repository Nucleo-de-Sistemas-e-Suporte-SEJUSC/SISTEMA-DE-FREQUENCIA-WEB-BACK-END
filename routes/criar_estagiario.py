from validators.criar_estagiario_validator import validator_estagiario as validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 

bp_criar_estagiario = Blueprint('bp_criar_estagiario', __name__)

@bp_criar_estagiario.route('/api/estagiarios', methods=['POST'])

def criar_estagiario():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        body = request.json
        validate = validator.validate(body)
            
        if validate == False:
                return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400
    
        setor = body.get('setor')
        nome = body.get('nome')
        cargo = body.get('cargo')
        horario = body.get('horario')
        horarioentrada = body.get('entrada')
        horariosaida = body.get('saida')
        #feriasinicio = body.get('feriasinicio')
        #feriasfinal = body.get('feriasfinal')
    
        verifica_se_estagiario_existe = "SELECT * FROM estagiarios WHERE nome = %s"
        cursor.execute(verifica_se_estagiario_existe, (nome,))
        estagiario = cursor.fetchone()
    
        if estagiario:
                conexao.close()
                return jsonify({'erro': 'Estagiário já cadastrado'}), 409
    
        criar_dados_estagiario = """
                INSERT INTO estagiarios (setor, nome,cargo,horario,horario_entrada,horario_saida)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
        cursor.execute(criar_dados_estagiario, (setor, nome, cargo,horario,horarioentrada, horariosaida))
        conexao.commit()
        conexao.close()
            
        dados_retornados = {
                "id": cursor.lastrowid,
                "setor": setor,
                "nome": nome,
                "cargo": cargo,
                "horario": horario,
                "horarioentrada": horarioentrada,
                "horariosaida": horariosaida,
                #"feriasinicio": feriasinicio,
                #"feriasfinal": feriasfinal
        }
        
        return jsonify(dados_retornados), 201
    except Error as e:
        return jsonify({'erro': 'Erro ao criar estagiário', 'mensagem': str(e)}), 500
