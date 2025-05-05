from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os
import re

bp_send_servidor_pdf = Blueprint('bp_send_servidor_pdf', __name__)

# Função comum
def download_zip(mes, tipo):
    try:
        ids = request.args.get('ids', '')
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        query = """
            SELECT caminho_zip 
            FROM arquivos_zip 
            WHERE mes = %s 
            AND tipo = %s
            ORDER BY id DESC 
            LIMIT 1
        """
        cursor.execute(query, (mes, tipo))
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
            download_name=f'frequencias_{mes}_{tipo}.zip'
        )
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    
    # Rota para servidores (mantém a existente)
@bp_send_servidor_pdf.route('/api/servidores/pdf/download-zip/<mes>', methods=['GET'])
def download_zip_servidores(mes):
    return download_zip(mes, 'servidores')

# Nova rota para estagiários
@bp_send_servidor_pdf.route('/api/estagiarios/pdf/download-zip/<mes>', methods=['GET'])
def download_zip_estagiarios(mes):
    return download_zip(mes, 'estagiario')
    