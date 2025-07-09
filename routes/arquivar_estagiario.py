from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 

bp_arquivar_estagiario = Blueprint('bp_arquivar_estagiario', __name__)

@bp_arquivar_estagiario.route('/api/estagiarios/<int:id>/arquivar', methods=['PATCH'])
#@login_required
#@roles_required('admin')
def arquivar_estagiario(id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        
        verifica_se_estagiario_existe = "SELECT * FROM estagiarios WHERE id = %s"
        cursor.execute(verifica_se_estagiario_existe, (id,))
        estagiario = cursor.fetchone()
        
        if estagiario is None:
            conexao.close()
            return jsonify({'erro': 'Estagiário não encontrado'}), 404
        
        arquivar_estagiario = """
            UPDATE estagiarios
            SET status = 'arquivado'
            WHERE id = %s
        """
        
        cursor.execute(arquivar_estagiario, (id,))
        conexao.commit()
        conexao.close()
        
        return jsonify({'mensagem': 'Estagiário arquivado com sucesso', 'estagiario_arquivado': {
            'nome': estagiario['nome'] ,
            'setor': estagiario['setor'] ,
        } ,
        }), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
