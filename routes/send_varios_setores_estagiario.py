from flask import send_file, Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os

bp_send_varios_setores_estagiarios_pdf = Blueprint('bp_send_varios_setores_estagiarios_pdf', __name__)

@bp_send_varios_setores_estagiarios_pdf.route('/api/setores/estagiarios/pdf/download-zip-multiestagiarios/<mes>', methods=['GET'])
def download_zip_multiestagiarios_estagiarios(mes): # Função renomeada
    try:
        mes_formatado = mes.capitalize()
        print(f"DEBUG: Buscando arquivo multiestagiarios para mês: {mes_formatado}")
        
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT caminho_zip FROM arquivos_zip WHERE mes=%s AND tipo='multiestagiarios_geral' AND setor='multiestagiarios' ORDER BY id DESC LIMIT 1",
            (mes_formatado,)
        )
        result = cursor.fetchone()

        print(f"DEBUG: Resultado da consulta: {result}")

        if not result:
            if conexao.is_connected():
                conexao.close()
            return jsonify({'erro': 'Arquivo ZIP multi-setores de estagiários não encontrado no banco de dados'}), 404

        zip_path_from_db = result["caminho_zip"]
        zip_path_verified = os.path.normpath(zip_path_from_db)

        print(f"DEBUG: Caminho do arquivo no DB: '{zip_path_from_db}'")
        print(f"DEBUG: Caminho verificado: '{zip_path_verified}'")
        print(f"DEBUG: Arquivo existe? {os.path.exists(zip_path_verified)}")

        if not os.path.exists(zip_path_verified):
            if conexao.is_connected():
                conexao.close()
            return jsonify({
                'erro': 'Arquivo físico não encontrado no servidor.',
                'caminho_esperado': zip_path_verified,
                'dados_banco': result,
                'mensagem': 'O arquivo ZIP de múltiplos setores só é criado quando há mais de um setor sendo processado'
            }), 404

        download_name = os.path.basename(zip_path_verified) 
        if conexao.is_connected():
            conexao.close()

        print(f"DEBUG: Enviando arquivo: {zip_path_verified}")
        return send_file(
            zip_path_verified,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()
        return jsonify({'erro': f'Erro ao baixar ZIP multi-setores de estagiários: {str(e)}'}), 500