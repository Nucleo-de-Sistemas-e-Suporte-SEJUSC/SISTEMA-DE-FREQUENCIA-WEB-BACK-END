import os
from flask import Blueprint, jsonify, send_file
from conection_mysql import connect_mysql
from flask_login import login_required

bp_send_ficha_funcional = Blueprint('bp_send_ficha_funcional', __name__)

@bp_send_ficha_funcional.route("/api/fichas-funcionais/download/<int:documento_id>", methods=["GET"])
# @login_required 
# Descomente a linha acima se o download exigir que o usuário esteja logado
def send_ficha_funcional(documento_id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        
        # Busca o documento, garantindo que seja do tipo "Ficha Funcional"
        query = """
            SELECT caminho_arquivo, nome_original FROM documentos 
            WHERE id = %s AND tipo_documento = 'Ficha Funcional'
        """
        cursor.execute(query, (documento_id,))
        documento = cursor.fetchone()
        
        cursor.close()
        conexao.close()

        if not documento:
            return jsonify({"erro": "Ficha Funcional não encontrada ou o ID não corresponde a este tipo de documento."}), 404

        caminho_arquivo = documento['caminho_arquivo']
        nome_original = documento['nome_original']

        if os.path.exists(caminho_arquivo):
            return send_file(caminho_arquivo, as_attachment=True, download_name=nome_original)
        else:
            return jsonify({"erro": "Arquivo não encontrado no servidor."}), 404

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro: {str(e)}"}), 500