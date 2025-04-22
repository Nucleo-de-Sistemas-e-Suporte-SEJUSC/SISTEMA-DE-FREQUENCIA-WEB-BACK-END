from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

@bp_send_setor_pdf.route('/api/setores/pdf/download-zip/<setor>/<mes>', methods=['GET'])
@bp_send_setor_pdf.route('/api/setores/estagiarios/pdf/download-zip/<setor>/<mes>', methods=['GET'])
def download_zip(setor, mes):
    try:
        # Normaliza o mês para garantir a primeira letra maiúscula
        mes_formatado = mes.capitalize()
        print(f"Setor recebido: {setor}, Mês formatado: {mes_formatado}")

        # Verifica se a rota chamada é a de estagiários
        is_estagiarios = 'estagiarios' in request.path.lower()

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Consulta SQL modificada para filtrar por tipo se necessário
        if is_estagiarios:
            cursor.execute(
                "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND tipo='estagiarios'", 
                (setor, mes_formatado)
            )
            download_prefix = 'frequencia_estagiarios'
        else:
            cursor.execute(
                "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND (tipo IS NULL OR tipo != 'estagiarios')", 
                (setor, mes_formatado)
            )
            download_prefix = 'frequencia_mensal'

        result = cursor.fetchone()
        
        if not result:
            error_msg = f"Arquivo ZIP não encontrado para setor={setor} e mes={mes_formatado}"
            print(error_msg)
            return jsonify({'erro': error_msg}), 404

        zip_path = result['caminho_zip']
        
        # Verifica se o caminho existe (com tratamento multiplataforma para barras)
        zip_path_verified = os.path.normpath(zip_path)
        if not os.path.exists(zip_path_verified):
            error_msg = f"Arquivo não encontrado no caminho: {zip_path_verified}"
            print(error_msg)
            return jsonify({'erro': error_msg}), 404

        print(f"Enviando arquivo ZIP: {zip_path_verified}")
        
        return send_file(
            zip_path_verified,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{download_prefix}_{setor}_{mes_formatado}.zip'
        )
    except Exception as e:
        error_msg = f'Erro ao enviar o arquivo ZIP: {str(e)}'
        print(error_msg)
        return jsonify({'erro': error_msg}), 500
    finally:
        if 'conexao' in locals():
            conexao.close()