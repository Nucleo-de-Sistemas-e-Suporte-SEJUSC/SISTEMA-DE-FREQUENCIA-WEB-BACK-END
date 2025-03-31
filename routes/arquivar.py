from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 

bp_arquivar_servidor = Blueprint('bp_arquivar_servidor', __name__)

# Rota para arquivar um servidor (funcionário)
@bp_arquivar_servidor.route('/api/servidores/<int:id>/arquivar', methods=['PATCH'])
# @login_required
# @roles_required('admin')
def arquivar_servidor(id):
    print("Cheguei aqui")
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o servidor (funcionário) existe
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
        print(arquivar_servidor)
        cursor.execute(arquivar_servidor, (id,))
        conexao.commit()
        conexao.close()

        return jsonify({'mensagem': 'Servidor arquivado com sucesso'}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
