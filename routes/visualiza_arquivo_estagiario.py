from flask import send_file, Blueprint, request, jsonify
import os

bp_visualiza_pdf_arquivo_estagiario = Blueprint('bp_visualiza_pdf_arquivo_estagiario', __name__)

@bp_visualiza_pdf_arquivo_estagiario.route('/api/estagiarios/pdf/view', methods=['GET'])
def view_pdf_arquivo():
    try:
        setor = request.args.get('setor')
        mes = request.args.get('mes')
        nome = request.args.get('nome')

        if not setor or not mes or not nome:
            return jsonify({'erro': 'Parâmetros setor, mes e nome são obrigatórios'}), 400
        

        BASE_DIR = f"setor/{setor}/estagiario/{mes}/{nome}/"

        nome_formatado = nome.replace(" ", "_")

        nome_arquivo = f"{nome_formatado}_FREQUENCIA.pdf"
        caminho_arquivo = os.path.join(BASE_DIR, nome_arquivo)

        caminho_arquivo = os.path.normpath(caminho_arquivo)
        
        if not os.path.exists(caminho_arquivo):
            return jsonify({'erro': 'Arquivo não encontrado'}), 404

        return send_file(
            caminho_arquivo,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=nome_arquivo
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
