from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

from flask import request, send_file, jsonify
import os

@bp_send_setor_pdf.route('/api/setores/download', methods=['GET'])
def send_setores():
    mes = request.args.get('mes')
    setor = request.args.get('setor')
    todos = request.args.get('todos')

    base_path = 'setor'

    if todos and mes:
        # Caminho do ZIP geral
        zip_path = os.path.join(base_path, f'frequencias_multissetores_{mes}.zip')
        if os.path.exists(zip_path):
            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f'frequencias_multissetores_{mes}.zip'
            )
        else:
            return jsonify({'erro': 'Arquivo ZIP geral não encontrado'}), 404

    elif setor and mes:
        # Caminho do ZIP individual do setor
        zip_path = os.path.join(base_path, setor, f'frequencias_{setor}_{mes}.zip')
        if os.path.exists(zip_path):
            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f'frequencias_{setor}_{mes}.zip'
            )
        else:
            return jsonify({'erro': 'Arquivo ZIP do setor não encontrado'}), 404

    else:
        return jsonify({'erro': 'Parâmetros inválidos'}), 400
