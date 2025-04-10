from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

@bp_send_setor_pdf.route('/api/setores/pdf/download-zip/<setor>/<mes>', methods=['GET'])
def download_zip(setor, mes):
    try:
        print(f"Setor recebido: {setor}, Mês recebido: {mes}")

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Consulta SQL para buscar o caminho do ZIP
        cursor.execute("SELECT caminho_zip FROM arquivos_zip_setores WHERE setor=%s AND mes=%s", (setor, mes))
        result = cursor.fetchone()

        if not result or not os.path.exists(result['caminho_zip']):
            print(f"Arquivo ZIP não encontrado para setor={setor} e mes={mes}")
            return jsonify({'erro': 'Arquivo ZIP não encontrado'}), 404

        zip_path = result['caminho_zip']
        print(f"Enviando arquivo ZIP: {zip_path}")
        
        return send_file(zip_path, mimetype='application/zip', as_attachment=True,
                         download_name=f'{setor}_{mes}_frequencia_mensal.zip')
    except Exception as e:
        print(f"Erro ao enviar o arquivo ZIP: {e}")
        return jsonify({'erro': f'Erro ao enviar o arquivo ZIP: {str(e)}'}), 500