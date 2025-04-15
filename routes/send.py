from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os
import re

bp_send_servidor_pdf = Blueprint('bp_send_servidor_pdf', __name__)

@bp_send_servidor_pdf.route('/api/servidores/pdf/download-zip/<mes>', methods=['GET'])
def download_zip(mes):
    try:
        ids_servidores = request.args.get('ids', '')
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Busca o ZIP mais recente para esses IDs e mês
        query = """
            SELECT caminho_zip 
            FROM arquivos_zip 
            WHERE mes = %s 
            ORDER BY id DESC 
            LIMIT 5
        """
        cursor.execute(query, (mes, ids_servidores))
        result = cursor.fetchone()

        if not result:
            return jsonify({'erro': 'Arquivo ZIP não encontrado'}), 404
            
        zip_path = os.path.normpath(result["caminho_zip"])
        
        if not os.path.exists(zip_path):
            return jsonify({'erro': 'Arquivo não existe no servidor'}), 404

        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'frequencias_{mes}.zip'
        )
    except Exception as e:
        return jsonify({'erro': str(e)}), 500