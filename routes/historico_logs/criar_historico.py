from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql

bp_criar_historico = Blueprint('bp_criar_historico', __name__)

@bp_criar_historico.route('/api/historico-logs', methods=['POST'])
def criar_historico():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        data = request.json
        mensagem = data.get('mensagem')
        nome = data.get('nome')
        acao = data.get('acao')

        if not mensagem or not nome or not acao:
            return jsonify({'erro': 'Dados incompletos'}), 400

        cria_historico_logs = """
            INSERT INTO historico_logs (mensagem, nome, acao)
            VALUES (%s, %s, %s)
        """
        cursor.execute(cria_historico_logs, (mensagem, nome, acao))
        conexao.commit()
        conexao.close()

        dados_retornados = {
            "id": cursor.lastrowid,
            "nome": nome,
            "mensagem": mensagem,
            "acao": acao,
        } 

        return jsonify({'servidor': dados_retornados}), 201
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
        
