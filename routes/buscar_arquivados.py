from flask import jsonify, Blueprint
from datetime import timedelta
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required   # Importa o decorador personalizado


bp_buscar_servidores_arquivados = Blueprint('bp_buscar_servidores_arquivados', __name__)

def timedelta_to_str(td):
    """Converte timedelta em string no formato HH:MM:SS"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@bp_buscar_servidores_arquivados.route('/api/servidores/arquivados', methods=['GET'])
# @login_required
# @roles_required('admin','editor')
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

        for servidor in servidores_arquivados:
            for key, value in servidor.items():
                if isinstance(value, timedelta):
                    servidor[key] = timedelta_to_str(value)
        
        return jsonify({"servidores": servidores_arquivados}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
