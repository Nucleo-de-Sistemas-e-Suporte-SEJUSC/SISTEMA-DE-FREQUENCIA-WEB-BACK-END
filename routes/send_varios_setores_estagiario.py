from flask import send_file, Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os

bp_send_varios_setores_estagiarios_pdf = Blueprint('bp_send_varios_setores_estagiarios_pdf', __name__)

@bp_send_varios_setores_estagiarios_pdf.route('/api/setores/estagiarios/pdf/download-zip-multiestagiarios/<mes>', methods=['GET'])
def download_zip_multiestagiarios_estagiarios(mes): # Função renomeada
    try:
        mes_formatado = mes.capitalize()
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Busca o ZIP mais recente de multiestagiarios para o mês
        # Nota: setor é 'multiestagiarios' e tipo é 'multiestagiarios' conforme a lógica de geração
        cursor.execute(
            "SELECT caminho_zip FROM arquivos_zip WHERE mes=%s AND tipo='multiestagiarios_geral' AND setor='multiestagiarios' ORDER BY id DESC LIMIT 1",
            (mes_formatado,)
        )
        result = cursor.fetchone()

        if not result:
            if conexao.is_connected():
                conexao.close()
            return jsonify({'erro': 'Arquivo ZIP multi-setores de estagiários não encontrado'}), 404

        zip_path_from_db = result["caminho_zip"]
        zip_path_verified = os.path.normpath(zip_path_from_db)

        print(f"Tentando acessar arquivo ZIP (multiestagiarios) no caminho: {zip_path_verified}")

        if not os.path.exists(zip_path_verified):
            if conexao.is_connected():
                conexao.close()
            return jsonify({
                'erro': 'Arquivo físico (multiestagiarios) não encontrado no servidor.',
                'caminho_esperado': zip_path_verified,
                'dados_banco': result
            }), 404

        download_name = os.path.basename(zip_path_verified) # Usa o nome real do arquivo do caminho
        # Ou, se você quiser um esquema de nomenclatura consistente para download:
        # download_name = f'frequencias_multissetores_estagiarios_{mes_formatado}.zip'

        if conexao.is_connected():
            conexao.close()

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