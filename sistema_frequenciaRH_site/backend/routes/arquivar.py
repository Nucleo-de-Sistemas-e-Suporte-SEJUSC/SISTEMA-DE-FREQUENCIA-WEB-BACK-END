from flask import jsonify, request, Blueprint
from conection import conect
from mysql.connector import Error

bp_arquivar_servidor = Blueprint('bp_arquivar_servidor', __name__)

# Rota para arquivar um servidor
@bp_arquivar_servidor.route('/api/servidores/<int:id>/arquivar', methods=['PATCH'])
def arquivar_servidor(id):
    try:
        conexao = conect()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o servidor existe
        verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE id = %s"
        cursor.execute(verifica_se_servidor_existe, (id,))
        servidor = cursor.fetchone()
        print(servidor)

        if servidor is None:
            conexao.close()
            return jsonify({'erro': 'Servidor não encontrado'}), 404

        # Atualiza o status do servidor para "arquivado"
        arquivar_servidor = """
            UPDATE funcionarios
            SET status = 'arquivado'
            WHERE id = %s
        """
        cursor.execute(arquivar_servidor, (id,))
        conexao.commit()
        conexao.close()

        return jsonify({'mensagem': 'Servidor arquivado com sucesso'}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
