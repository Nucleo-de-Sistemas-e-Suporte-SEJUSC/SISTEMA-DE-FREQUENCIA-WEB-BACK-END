from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

@bp_send_setor_pdf.route('/api/setores/pdf/download-zip/<setor>/<mes>', methods=['GET'])
@bp_send_setor_pdf.route('/api/setores/estagiarios/<setor>/<mes>', methods=['GET'])
def download_zip(setor, mes):
    try:
        setor_para_consulta_db = setor.replace('_', '/')
        mes_formatado = mes.capitalize()
        is_estagiarios = 'estagiarios' in request.path.lower()
        
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        query = ""
        if is_estagiarios:
            query = "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND tipo='estagiarios_setor' LIMIT 1"
        else:
            query = "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND (tipo IS NULL OR tipo != 'estagiarios_setor') LIMIT 1"
        
        params = (setor_para_consulta_db, mes_formatado)
        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            return jsonify({'erro': 'Arquivo ZIP não encontrado no banco de dados'}), 404

        caminho_relativo_do_db = result["caminho_zip"]

        # Sobe um nível para ir do diretório 'routes' para a raiz do projeto.
        caminho_base_do_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Junta o caminho base do projeto com o caminho relativo do banco de dados.
        caminho_absoluto_final = os.path.join(caminho_base_do_projeto, caminho_relativo_do_db)

        print(f"Caminho relativo do DB: '{caminho_relativo_do_db}'")
        print(f"Caminho base descoberto dinamicamente: '{caminho_base_do_projeto}'")
        print(f"Caminho absoluto final para o arquivo: '{caminho_absoluto_final}'")

        if not os.path.exists(caminho_absoluto_final):
            print(f"ERRO FÍSICO: Arquivo não encontrado em '{caminho_absoluto_final}'")
            return jsonify({'erro': 'Arquivo físico não encontrado no servidor.'}), 404

        # **CORREÇÃO:** Obtém o nome do arquivo diretamente do caminho completo.
        # Isso garante que o nome do arquivo seja exatamente como está no sistema de arquivos.
        download_name = os.path.basename(caminho_absoluto_final)
        
        return send_file(
            caminho_absoluto_final,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()
            print("Conexão com DB fechada.")