from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

@bp_send_setor_pdf.route('/api/setores/pdf/download-zip/<setor>/<mes>', methods=['GET'])
@bp_send_setor_pdf.route('/api/setores/estagiarios/pdf/download-zip/<setor>/<mes>', methods=['GET'])
def download_zip(setor, mes):
    try:
        mes_formatado = mes.capitalize()
        is_estagiarios = 'estagiarios' in request.path.lower()

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        if is_estagiarios:
            cursor.execute(
                "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND tipo='estagiarios'", 
                (setor, mes_formatado)
            )
        else:
            cursor.execute(
                "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND (tipo IS NULL OR tipo != 'estagiarios')", 
                (setor, mes_formatado)
            )

        result = cursor.fetchone()
        
        if not result:
            return jsonify({'erro': 'Arquivo ZIP não encontrado no banco de dados'}), 404

        # Usa o caminho EXATO do banco de dados
        zip_path = result["caminho_zip"]
        zip_path_verified = os.path.normpath(zip_path)
        
        print(f"Tentando acessar arquivo ZIP no caminho: {zip_path_verified}")
        
        if not os.path.exists(zip_path_verified):
            return jsonify({
                'erro': f'Arquivo físico não encontrado',
                'caminho_esperado': zip_path_verified,
                'dados_banco': result
            }), 404

        # Mantém o nome de download consistente
        download_name = f'frequencias_{setor}_{mes_formatado}.zip'
        if is_estagiarios:
            download_name = f'frequencias_estagiarios_{setor}_{mes_formatado}.zip'

        return send_file(
            zip_path_verified,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'conexao' in locals():
            conexao.close()