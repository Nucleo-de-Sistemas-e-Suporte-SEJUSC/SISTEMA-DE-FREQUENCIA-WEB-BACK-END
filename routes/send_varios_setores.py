from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os

bp_send_varios_setores_pdf = Blueprint('bp_send_varios_setores_pdf', __name__)

@bp_send_varios_setores_pdf.route('/api/setores/pdf/download-zip-multissetores/<mes>', methods=['GET'])
def download_zip_multissetores(mes):
    try:
        mes_formatado = mes.capitalize()
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Busca o ZIP mais recente de multissetores para o mês
        cursor.execute(
            "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s ORDER BY id DESC LIMIT 1",
            ('multissetores', mes_formatado)
        )
        result = cursor.fetchone()
        if not result:
            return jsonify({'erro': 'Arquivo ZIP multissetores não encontrado'}), 404

        zip_path = os.path.normpath(result["caminho_zip"])
        if not os.path.exists(zip_path):
            return jsonify({'erro': 'Arquivo físico não encontrado', 'caminho_esperado': zip_path}), 404

        download_name = f'frequencias_multissetores_{mes_formatado}.zip'
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
