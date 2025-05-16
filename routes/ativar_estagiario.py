from flask import jsonify, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 


bp_ativar_estagiario = Blueprint('bp_ativar_estagiario', __name__) 

@bp_ativar_estagiario.route('/api/estagiarios/<int:id>/atualizar-status', methods=['PATCH'])
def ativar_estagiario(id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o estagiário existe
        verifica_se_estagiario_existe = "SELECT * FROM estagiarios WHERE id = %s"
        cursor.execute(verifica_se_estagiario_existe, (id,))
        estagiario = cursor.fetchone()

        if estagiario is None:
            conexao.close()
            return jsonify({'erro': 'Estagiário não encontrado'}), 404

        # Defina o novo status como "ativo"
        novo_status = 'ativo'

        # Atualiza o status do estagiário
        atualizar_status = """
            UPDATE estagiarios
            SET status = %s
            WHERE id = %s
        """
        cursor.execute(atualizar_status, (novo_status, id))
        conexao.commit()
        conexao.close()
        print(estagiario)
        return jsonify({'mensagem': 'Status do estagiário atualizado com sucesso', "estagiario_ativado": {
            "nome": estagiario['nome'],
            "setor": estagiario['setor'],
        }}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500