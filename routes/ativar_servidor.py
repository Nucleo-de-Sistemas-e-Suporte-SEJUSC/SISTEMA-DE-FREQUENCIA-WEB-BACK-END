from flask import jsonify, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error

bp_atualizar_servidor_status = Blueprint('bp_atualizar_servidor_status', __name__)

@bp_atualizar_servidor_status.route('/api/servidores/<int:id>/atualizar-status', methods=['PATCH'])
def atualizar_status_servidor(id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o servidor existe
        verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE id = %s"
        cursor.execute(verifica_se_servidor_existe, (id,))
        servidor = cursor.fetchone()
        print(servidor)

        if servidor is None:
            conexao.close()
            return jsonify({'erro': 'Servidor não encontrado'}), 404

        # Defina o novo status como "ativo"
        novo_status = 'ativo'

        # Atualiza o status do servidor
        atualizar_status = """
            UPDATE funcionarios
            SET status = %s
            WHERE id = %s
        """
        cursor.execute(atualizar_status, (novo_status, id))
        conexao.commit()
        conexao.close()

        return jsonify({'mensagem': 'Status do servidor atualizado com sucesso'}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
