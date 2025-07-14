import os
import uuid
from flask import Blueprint, jsonify
from conection_mysql import connect_mysql
from utils.gerador_excel import preencher_ficha_excel
from utils.convert_to_pdf import convert_to_pdf

bp_gerar_ficha_funcional = Blueprint("bp_gerar_ficha_funcional", __name__)

UPLOADS_FOLDER = os.path.join(os.getcwd(), "uploads")
TEMP_FOLDER = os.path.join(os.getcwd(), "temp_files")

os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@bp_gerar_ficha_funcional.route("/api/servidores/<int:funcionario_id>/gerar-ficha-funcional", methods=["POST"])
def gerar_ficha(funcionario_id):
    conexao = None
    cursor = None
    temp_xlsx_path = None
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # 1. BUSCA OS DADOS PRINCIPAIS DO FUNCIONÁRIO
        cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (funcionario_id,))
        funcionario = cursor.fetchone()

        if not funcionario:
            return jsonify({"erro": "Funcionário não encontrado"}), 404

        # 2. (NOVA LÓGICA) BUSCA A LISTA DE BENEFICIÁRIOS
        cursor.execute("SELECT nome, parentesco, data_nascimento FROM beneficiarios WHERE funcionario_id = %s", (funcionario_id,))
        beneficiarios_list = cursor.fetchall()
        
        # Adiciona a lista de beneficiários ao dicionário do funcionário
        funcionario['beneficiarios'] = beneficiarios_list

        template_path = "FICHA_FUNCIONAL_TEMPLATE.xlsx"
        if not os.path.exists(template_path):
            return jsonify({"erro": f"Template '{template_path}' não encontrado."}), 500

        # O resto do fluxo continua o mesmo...
        temp_xlsx_name = f"{uuid.uuid4()}.xlsx"
        temp_xlsx_path = os.path.join(TEMP_FOLDER, temp_xlsx_name)

        sucesso, erro = preencher_ficha_excel(template_path, funcionario, temp_xlsx_path)
        if not sucesso:
            return jsonify({"erro": "Falha ao preencher a planilha", "detalhe": erro}), 500

        pdf_path = convert_to_pdf(temp_xlsx_path, UPLOADS_FOLDER)
        if not pdf_path:
             return jsonify({"erro": "Falha ao converter o arquivo para PDF"}), 500
        
        nome_original_pdf = f"Ficha_Funcional_{funcionario['nome'].replace(' ', '_')}.pdf"
        nome_armazenado_pdf = os.path.basename(pdf_path)

        query = """
            INSERT INTO documentos 
            (nome_original, nome_armazenado, caminho_arquivo, tipo_documento, funcionario_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome_original_pdf, nome_armazenado_pdf, pdf_path, "Ficha Funcional", funcionario_id))
        conexao.commit()
        documento_id = cursor.lastrowid
        
        return jsonify({
            "mensagem": "Ficha Funcional gerada com sucesso!",
            "documento_id": documento_id
        }), 201

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro inesperado: {str(e)}"}), 500
    
    finally:
        if temp_xlsx_path and os.path.exists(temp_xlsx_path):
            os.remove(temp_xlsx_path)
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()