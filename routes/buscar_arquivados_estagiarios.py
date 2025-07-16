from flask import jsonify, Blueprint
from datetime import timedelta
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required
from decorador import roles_required   

bp_buscar_estagiarios_arquivados = Blueprint('bp_buscar_estagiarios_arquivados', __name__)
def timedelta_to_str(td):
   
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@bp_buscar_estagiarios_arquivados.route('/api/estagiarios/arquivados', methods=['GET'])
def buscar_estagiarios_arquivados():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        buscar_estagiarios_arquivados = """
            SELECT * FROM estagiarios
            WHERE status = 'arquivado'
        """
        cursor.execute(buscar_estagiarios_arquivados)
        estagiarios_arquivados = cursor.fetchall()
        conexao.close()

        for estagiario in estagiarios_arquivados:
            for key, value in estagiario.items():
                if isinstance(value, timedelta):
                    estagiario[key] = timedelta_to_str(value)
        
        return jsonify({"estagiarios": estagiarios_arquivados}), 200
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500