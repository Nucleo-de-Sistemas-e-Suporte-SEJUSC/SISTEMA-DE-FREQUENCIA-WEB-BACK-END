from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os

bp_send_varios_setores_pdf = Blueprint('bp_send_varios_setores_pdf', __name__)

@bp_send_varios_setores_pdf.route('/api/setores/pdf/download-zip-multissetores/<mes>', methods=['GET'])
def download_zip_multissetores(mes):
    try:
        mes_formatado = mes.capitalize()
        print(f"DEBUG: Buscando arquivo multissetores para mês: {mes_formatado}")
        
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT caminho_zip FROM arquivos_zip WHERE mes = %s AND tipo = 'multissetores_funcionarios_geral' ORDER BY id DESC LIMIT 1",
            (mes_formatado,)
        )
        
        result = cursor.fetchone()
        print(f"DEBUG: Resultado da consulta: {result}")
        
        if not result:
            return jsonify({'erro': 'Arquivo ZIP multissetores não encontrado no banco de dados'}), 404

        zip_path = os.path.normpath(result["caminho_zip"])
        print(f"DEBUG: Caminho do arquivo no DB: '{result['caminho_zip']}'")
        print(f"DEBUG: Caminho verificado: '{zip_path}'")
        print(f"DEBUG: Arquivo existe? {os.path.exists(zip_path)}")
        
        if not os.path.exists(zip_path):
            return jsonify({
                'erro': 'Arquivo físico não encontrado no servidor.',
                'caminho_esperado': zip_path,
                'dados_banco': result,
                'mensagem': 'O arquivo ZIP de múltiplos setores só é criado quando há mais de um setor sendo processado'
            }), 404

        download_name = f'frequencias_multissetores_{mes_formatado}.zip'
        print(f"DEBUG: Enviando arquivo: {zip_path}")
        
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'conexao' in locals():
            conexao.close()
