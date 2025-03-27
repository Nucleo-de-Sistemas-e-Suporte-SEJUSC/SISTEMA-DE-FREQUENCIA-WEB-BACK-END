from flask import jsonify, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required   # Importa o decorador personalizado


bp_buscar_servidores_arquivados = Blueprint('bp_buscar_servidores_arquivados', __name__)

@bp_buscar_servidores_arquivados.route('/api/servidores/arquivados', methods=['GET'])
@login_required
@roles_required('admin','editor')
def buscar_servidores_arquivados():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Consulta para buscar todos os servidores arquivados
        buscar_servidores_arquivados = """
            SELECT * FROM funcionarios
            WHERE status = 'arquivado'
        """
        cursor.execute(buscar_servidores_arquivados)
        servidores_arquivados = cursor.fetchall()
        
        conexao.close()

        return jsonify(servidores_arquivados), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
