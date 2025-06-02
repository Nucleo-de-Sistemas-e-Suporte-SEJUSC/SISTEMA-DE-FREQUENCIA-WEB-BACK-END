from flask import send_file
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
import os 

bp_send_setor_pdf = Blueprint('bp_send_setor_pdf', __name__)

@bp_send_setor_pdf.route('/api/setores/pdf/download-zip/<setor>/<mes>', methods=['GET'])
@bp_send_setor_pdf.route('/api/setores/estagiarios/<setor>/<mes>', methods=['GET'])
def download_zip(setor, mes):
    try:
        # --- INÍCIO DA TRANSFORMAÇÃO ---
        # Se na URL você usa '_' para representar '/', converta aqui:
        setor_para_consulta_db = setor.replace('_', '/')
        # Se você usa outra convenção na URL, ajuste a lógica de substituição.
        # Por exemplo, se na URL é 'SETORPARTE1PARTE2' e no BD é 'SETOR/PARTE1/PARTE2',
        # a transformação seria mais complexa e dependeria de regras fixas.
        # A substituição de '_' por '/' é a mais provável e simples.
        # --- FIM DA TRANSFORMAÇÃO ---

        mes_formatado = mes.capitalize()
        is_estagiarios = 'estagiarios' in request.path.lower()

        # Logs para depuração (muito importantes!)
        print(f"Setor recebido da URL: '{setor}'")
        print(f"Setor transformado para consulta DB: '{setor_para_consulta_db}'")
        print(f"Mês formatado para consulta DB: '{mes_formatado}'")
        print(f"É estagiário? {is_estagiarios}")

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        query = ""
        params = ()

        if is_estagiarios:
            query = "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND tipo='estagiarios'"
            params = (setor_para_consulta_db, mes_formatado) # Use a variável transformada!
        else:
            query = "SELECT caminho_zip FROM arquivos_zip WHERE setor=%s AND mes=%s AND (tipo IS NULL OR tipo != 'estagiarios')"
            params = (setor_para_consulta_db, mes_formatado) # Use a variável transformada!

        print(f"Executando SQL: {query} com params: {params}") # Log da consulta
        cursor.execute(query, params)
        result = cursor.fetchone()

        if not result:
            print("RESULTADO DA CONSULTA: Arquivo ZIP não encontrado no banco de dados.") # Log específico
            return jsonify({'erro': 'Arquivo ZIP não encontrado no banco de dados para os critérios fornecidos'}), 404

        zip_path_from_db = result["caminho_zip"]
        zip_path_verified = os.path.normpath(zip_path_from_db) # Use o caminho EXATO do DB

        print(f"Caminho do arquivo no DB: '{zip_path_from_db}'")
        print(f"Tentando acessar arquivo ZIP no caminho verificado: '{zip_path_verified}'")

        if not os.path.exists(zip_path_verified):
            print(f"ERRO FÍSICO: Arquivo não encontrado em '{zip_path_verified}'") # Log específico
            return jsonify({
                'erro': f'Arquivo físico não encontrado no servidor.',
                'caminho_esperado_no_servidor': zip_path_verified,
                'dados_do_banco': result
            }), 404

        download_name = f'frequencias_{setor}_{mes_formatado}.zip' # O nome do download pode usar o 'setor' original da URL
        if is_estagiarios:
            download_name = f'frequencias_estagiarios_{setor}_{mes_formatado}.zip'

        return send_file(
            zip_path_verified,
            mimetype='application/zip',
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        print(f"Erro inesperado: {str(e)}") # Log de qualquer outra exceção
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()
            print("Conexão com DB fechada.")