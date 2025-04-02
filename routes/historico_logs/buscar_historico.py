from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql

bp_buscar_historico = Blueprint('bp_buscar_historico', __name__)

@bp_buscar_historico.route('/api/historico-logs', methods=['GET'])
def criar_historico():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        historico_logs = """
            SELECT * FROM historico_logs

        """
        cursor.execute(historico_logs)
        historico = cursor.fetchall()

        return jsonify({'historico': historico}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
        
