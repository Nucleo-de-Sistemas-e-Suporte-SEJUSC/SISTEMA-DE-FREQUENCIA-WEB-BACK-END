from flask import jsonify, request, Blueprint
from conection import conect
from mysql.connector import Error

bp_deletar_servidor = Blueprint('bp_deletar_servidor', __name__)


@bp_deletar_servidor.route('/api/servidores/<int:id>', methods=['DELETE'])
def deletar_servidor(id):
    try:
        conexao = conect()
        cursor = conexao.cursor(dictionary=True)

        verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE id = %s"
        cursor.execute(verifica_se_servidor_existe, (id,))
        servidor = cursor.fetchone()
        print(servidor)

        if servidor == None:
            conexao.close()
            return jsonify({'erro': 'Servidor não encontrado'}), 409

        deletar_servidor = """
            DELETE FROM funcionarios
            WHERE id = %s
        """
        cursor.execute(deletar_servidor, (id,))
        conexao.commit()
        conexao.close()

        return jsonify({'mensagem': 'Servidor deletado com sucesso'}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500