from flask import send_file, Blueprint, jsonify
from conection_mysql import connect_mysql
import os

bp_send_documentos = Blueprint('bp_send_documentos', __name__)

@bp_send_documentos.route('/api/documentos/download/<int:documento_id>', methods=['GET'])
def download_documento(documento_id):

    try:
        with connect_mysql() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query = "SELECT caminho_arquivo, nome_original FROM documentos WHERE id = %s"
                cursor.execute(query, (documento_id,))
                documento = cursor.fetchone()

        if not documento:
            return jsonify({'erro': 'Documento não encontrado no banco de dados'}), 404

        caminho_arquivo = documento['caminho_arquivo']
        nome_original_download = documento['nome_original']

        if not os.path.exists(caminho_arquivo):

            print(f"ERRO: Arquivo não encontrado no disco, mas existe no DB. ID: {documento_id}, Caminho: {caminho_arquivo}")
            return jsonify({'erro': 'Arquivo físico não encontrado no servidor'}), 404


        return send_file(
            caminho_arquivo,
            as_attachment=True,
            download_name=nome_original_download  # será enviado para o usuario, o nome do documento original que foi enviado para o banco de dados.
        )

    except Exception as e:
        print(f"Erro ao baixar documento: {e}")
        return jsonify({'erro': 'Erro interno ao processar o download'}), 500