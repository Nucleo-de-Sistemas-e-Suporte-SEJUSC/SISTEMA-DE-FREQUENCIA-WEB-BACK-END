from validators.criar_servidor_validator import validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection import conect
from mysql.connector import Error

bp_criar_servidor = Blueprint('bp_criar_servidor', __name__)


@bp_criar_servidor.route('/api/servidores', methods=['POST'])
def criar_servidor():
    try:
        conexao = conect()
        cursor = conexao.cursor(dictionary=True)
        body = request.json
        validate = validator.validate(body)
        
        if validate == False:
            return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400


        setor = body.get('setor')
        nome = body.get('nome')
        matricula = body.get('matricula')
        cargo = body.get('cargo')
        funcao = body.get('funcao')
        horario = body.get('horario')
        entrada = body.get('entrada')
        saida = body.get('saida')
        ferias_inicio = body.get('ferias_inicio')
        ferias_termino = body.get('ferias_termino')

        verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE nome = %s"
        cursor.execute(verifica_se_servidor_existe, (nome,))
        servidor = cursor.fetchone()

        if servidor:
            conexao.close()
            return jsonify({'erro': 'Servidor já cadastrado'}), 409

        criar_dados_servidor = """
            INSERT INTO funcionarios (setor, nome, matricula, cargo, funcao, horario, entrada, saida, ferias_inicio, ferias_termino)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(criar_dados_servidor, (setor, nome, matricula, cargo, funcao, horario, entrada, saida, ferias_inicio, ferias_termino,))
        conexao.commit()
        conexao.close()
        
        dados_retornados = {
            "id": cursor.lastrowid,
            "setor": setor,
            "nome": nome,
            "matricula": matricula,
            "cargo": cargo,
            "funcao": funcao,
            "horario": horario,
            "entrada": entrada,
            "saida": saida,
            "ferias_inicio": ferias_inicio,
            "ferias_termino": ferias_termino

        } 

        return jsonify({'servidor': dados_retornados}), 201
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500

