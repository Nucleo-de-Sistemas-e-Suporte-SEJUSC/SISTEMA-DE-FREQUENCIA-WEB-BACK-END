import os
import uuid
from flask import jsonify, request, Blueprint, send_from_directory
from werkzeug.utils import secure_filename
from conection_mysql import connect_mysql
   
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

    if 'file' not in request.files:
        return jsonify({"error": "Requisição inválida: o campo 'file' é obrigatório."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    tipo_documento = request.form.get('tipo_documento', 'Não especificado')
    funcionario_id = request.form.get('funcionario_id')
    estagiario_id = request.form.get('estagiario_id')

    if not funcionario_id and not estagiario_id:
        return jsonify({"error": "É necessário fornecer 'funcionario_id' ou 'estagiario_id'."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Tipo de arquivo não permitido."}), 400

    if file:

        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(UPLOADS_FOLDER, unique_filename)

        try:
       
            file.save(filepath)

            conn = connect_mysql()
            cursor = conn.cursor()

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
            cursor.close()
            conn.close()
            
            return jsonify({
                "message": "Documento enviado com sucesso!",
                "document_id": new_document_id,
                "filename": unique_filename
            }), 201

        except Exception as e:
    
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"Erro no upload: {e}") 
            return jsonify({"error": "Erro interno ao salvar o documento."}), 500
            
    return jsonify({"error": "Falha desconhecida no upload."}), 500
