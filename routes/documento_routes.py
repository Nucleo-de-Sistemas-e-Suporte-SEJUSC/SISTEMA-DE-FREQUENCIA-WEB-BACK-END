import os
import uuid
from flask import jsonify, request, Blueprint
from werkzeug.utils import secure_filename
from conection_mysql import connect_mysql 

bp_documentos = Blueprint('bp_documentos', __name__)

UPLOADS_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOADS_FOLDER):
    os.makedirs(UPLOADS_FOLDER)


ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_documentos.route('/api/documentos', methods=['POST'])
def upload_documento():
   
    if 'files' not in request.files:
        return jsonify({"error": "Requisição inválida: o campo 'files' é obrigatório."}), 400

    files = request.files.getlist('files') 

    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    tipos_documento = request.form.getlist('tipos_documento')
    
    if not tipos_documento:
        tipos_documento = ['Não especificado'] * len(files)
    
   
    while len(tipos_documento) < len(files):
        tipos_documento.append('Não especificado')

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

        for index, file in enumerate(files):
            if file.filename == '':
                continue 
            if not allowed_file(file.filename):
                errors.append(f"Tipo de arquivo não permitido para '{file.filename}'.")
                continue

            tipo_documento_atual = tipos_documento[index]

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

                cursor.execute(query, (original_filename, unique_filename, filepath, tipo_documento_atual, id_func, id_estag))
                conn.commit()

                new_document_id = cursor.lastrowid
                uploaded_documents_info.append({
                    "document_id": new_document_id,
                    "filename": unique_filename,
                    "original_filename": original_filename,
                    "tipo_documento": tipo_documento_atual,
                    "status": "success"
                })

            except Exception as e:
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                errors.append(f"Erro ao processar o arquivo '{original_filename}': {e}")
                print(f"Erro no upload para {original_filename}: {e}")
              
                if conn:
                    conn.rollback() 

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