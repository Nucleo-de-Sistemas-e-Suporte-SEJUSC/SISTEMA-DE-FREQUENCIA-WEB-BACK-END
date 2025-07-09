from validators.criar_estagiario_validator import validator_estagiario as validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 


bp_atualizar_estagiario = Blueprint('bp_atualizar_estagiario', __name__)

@bp_atualizar_estagiario.route('/api/estagiarios/<int:id>', methods=['PUT'])

def atualizar_estagiario(id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        body = request.json
        validate = validator.validate(body)
        
        if not validate:
            return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400

        setor = body.get('setor')
        nome = body.get('nome')
        cargo = body.get('cargo')
        horario = body.get('horario')
        horarioentrada = body.get('entrada')
        horariosaida = body.get('saida')
        feriasinicio = body.get('feriasinicio')
        feriasfinal = body.get('feriasfinal')

        verifica_se_estagiario_existe = "SELECT * FROM estagiarios WHERE id = %s"
        cursor.execute(verifica_se_estagiario_existe, (id,))
        estagiario = cursor.fetchone()

        if not estagiario:
            conexao.close()
            return jsonify({'erro': 'Estagiário não encontrado'}), 404

        atualizar_dados_estagiario = """
                UPDATE estagiarios 
                SET setor = %s, nome = %s, cargo = %s, horario = %s, horario_entrada = %s, horario_saida = %s, feriasinicio = %s, feriasfinal = %s
                WHERE id = %s
            """
        cursor.execute(atualizar_dados_estagiario, (setor, nome, cargo, horario, horarioentrada, horariosaida,feriasinicio,feriasfinal, id))
        conexao.commit()
        conexao.close()

        dados_retornados = {
            "id": id,
            "setor": setor,
            "nome": nome,
            "cargo": cargo,
            "horario": horario,
            "horarioentrada": horarioentrada,
            "horariosaida": horariosaida,
            "feriasinicio": feriasinicio,
            "feriasfinal": feriasfinal
        }
        
        return jsonify(dados_retornados), 200

    except Error as e:
        return jsonify({'erro': str(e)}), 500