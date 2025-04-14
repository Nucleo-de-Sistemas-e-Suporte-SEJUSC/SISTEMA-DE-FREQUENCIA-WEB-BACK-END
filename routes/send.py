from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os
import re

bp_send_servidor_pdf = Blueprint('bp_send_servidor_pdf', __name__)

@bp_send_servidor_pdf.route('/api/servidores/<nome>/pdf/download-zip/<mes>', methods=['GET'])
def download_zip(nome, mes):
    try:
        # Conexão com o banco de dados
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Busca o caminho do ZIP no banco de dados
        cursor.execute("SELECT caminho_zip FROM arquivos_zip WHERE mes = %s and nome = %s", (mes,nome,))
        result = cursor.fetchone()

        caminho_modificado = result["caminho_zip"].replace("/", "\\")

        if not result or not os.path.exists(caminho_modificado):
            conexao.close()
            return jsonify({'erro': 'Arquivo ZIP não encontrado'}), 404

    
        zip_path = caminho_modificado
        conexao.close()

        # Envia o arquivo ZIP ao frontend
        return send_file(zip_path, mimetype='application/zip', as_attachment=True, download_name=f'{mes}_frequencia_mensal.zip')
    except Exception as e:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro ao enviar o arquivo ZIP: {str(e)}'}), 500
