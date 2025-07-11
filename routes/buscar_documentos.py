import os
import uuid
from flask import jsonify, request, Blueprint
from werkzeug.utils import secure_filename
from conection_mysql import connect_mysql 

bp_buscar_documentos = Blueprint('bp_buscar_documentos', __name__)

@bp_buscar_documentos.route('/api/buscar/documentos', methods=['GET'])
def list_documentos():
    funcionario_id = request.args.get('funcionario_id', type=int)
    estagiario_id = request.args.get('estagiario_id', type=int)

    if not funcionario_id and not estagiario_id:
        return jsonify({'erro': 'É necessário fornecer um funcionario_id ou estagiario_id para listar documentos.'}), 400

    try:
        with connect_mysql() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query_params = []
                where_clauses = []

                if funcionario_id:
                    where_clauses.append("funcionario_id = %s")
                    query_params.append(funcionario_id)
                if estagiario_id:
                    where_clauses.append("estagiario_id = %s")
                    query_params.append(estagiario_id)

                where_sql = " AND ".join(where_clauses)
            
                query = "SELECT id, nome_original, tipo_documento, DATE_FORMAT(data_upload, '%%Y-%%m-%%d %%H:%%i:%%s') as data_upload FROM documentos"
                
                if where_sql:
                    query += f" WHERE {where_sql}" 

                print(f"DEBUG: Query gerada: {query}") 
                print(f"DEBUG: Parâmetros (query_params): {query_params}") 

                cursor.execute(query, tuple(query_params))
                documentos = cursor.fetchall()

        if not documentos:
            return jsonify({'mensagem': 'Nenhum documento encontrado para os IDs fornecidos.'}), 404

        return jsonify({'documentos': documentos}), 200

    except Exception as e:
        print(f"Erro ao listar documentos: {e}")
        return jsonify({'erro': 'Erro interno ao listar documentos.'}), 500