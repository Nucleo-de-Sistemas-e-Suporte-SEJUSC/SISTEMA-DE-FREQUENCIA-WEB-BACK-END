import os
import uuid
from flask import jsonify, request, Blueprint
from werkzeug.utils import secure_filename
from conection_mysql import connect_mysql # Assuming this is your database connection module

bp_documentos = Blueprint('bp_documentos', __name__)

UPLOADS_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOADS_FOLDER):
    os.makedirs(UPLOADS_FOLDER)

# Extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_documentos.route('/api/documentos', methods=['POST'])
def upload_documento():
    # Check if 'files' is in the request (plural for multiple files)
    if 'files' not in request.files:
        return jsonify({"error": "Requisição inválida: o campo 'files' é obrigatório."}), 400

    files = request.files.getlist('files') # Use getlist to get all files for the 'files' key

    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    tipo_documento = request.form.get('tipo_documento', 'Não especificado')
    funcionario_id = request.form.get('funcionario_id')
    estagiario_id = request.form.get('estagiario_id')

    if not funcionario_id and not estagiario_id:
        return jsonify({"error": "É necessário fornecer 'funcionario_id' ou 'estagiario_id'."}), 400

    uploaded_documents_info = []
    errors = []

    conn = None
    cursor = None

    try:
        conn = connect_mysql()
        cursor = conn.cursor()

        for file in files:
            if file.filename == '':
                continue # Skip empty file entries

            if not allowed_file(file.filename):
                errors.append(f"Tipo de arquivo não permitido para '{file.filename}'.")
                continue

            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{extension}"
            filepath = os.path.join(UPLOADS_FOLDER, unique_filename)

            try:
                file.save(filepath)

                query = """
                    INSERT INTO documentos
                    (nome_original, nome_armazenado, caminho_arquivo, tipo_documento, funcionario_id, estagiario_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                id_func = int(funcionario_id) if funcionario_id else None
                id_estag = int(estagiario_id) if estagiario_id else None

                cursor.execute(query, (original_filename, unique_filename, filepath, tipo_documento, id_func, id_estag))
                conn.commit()

                new_document_id = cursor.lastrowid
                uploaded_documents_info.append({
                    "document_id": new_document_id,
                    "filename": unique_filename,
                    "original_filename": original_filename,
                    "status": "success"
                })

            except Exception as e:
                # If there's an error saving/inserting for a specific file, try to clean up
                if os.path.exists(filepath):
                    os.remove(filepath)
                errors.append(f"Erro ao processar o arquivo '{original_filename}': {e}")
                print(f"Erro no upload para {original_filename}: {e}")
                # Don't commit if there was an error with this file, but continue with others if possible
                if conn:
                    conn.rollback() # Rollback the last operation if an error occurs for a single file

    except Exception as e:
        print(f"Erro geral no upload de múltiplos documentos: {e}")
        return jsonify({"error": "Erro interno ao processar os uploads.", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if uploaded_documents_info:
        response = {
            "message": "Upload de documentos concluído.",
            "uploaded_documents": uploaded_documents_info
        }
        if errors:
            response["warnings"] = errors
        return jsonify(response), 201
    else:
        return jsonify({"error": "Nenhum documento foi enviado ou todos falharam.", "details": errors}), 400