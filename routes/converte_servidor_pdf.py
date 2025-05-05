from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ROW_HEIGHT_RULE
import os
import zipfile 

bp_converte_servidor_pdf = Blueprint('bp_converte_servidor_pdf', __name__)

@bp_converte_servidor_pdf.route('/api/servidores/pdf', methods=['POST'])
def converte_servidor_pdf():
    try:
        body = request.json or {}
        funcionarios_id = body.get('funcionarios', [])
        print(funcionarios_id)

        if not funcionarios_id:
            return jsonify({'erro': 'Nenhum funcionário selecionado'}), 400

        try:
            ids = [int(id) for id in funcionarios_id]
        except ValueError:
            return jsonify({'erro': 'IDs inválidos'}), 400

        mes_body = body.get('mes')
        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ','.join(['%s'] * len(ids))
        query = f"SELECT * FROM funcionarios WHERE id IN ({placeholders})"
        cursor.execute(query, ids)
        funcionarios = cursor.fetchall()

        if not funcionarios:
            conexao.close()
            return jsonify({'erro': 'Nenhum funcionário encontrado'}), 404

        arquivos_gerados = []

        for funcionario in funcionarios:
            template_path = 'FREQUÊNCIA_MENSAL.docx'
            doc = Document(template_path)

            cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, funcionario)

            troca_de_dados = {
                "CAMPO SETOR": funcionario['setor'],
                "CAMPO MÊS": mes_por_extenso,
                "CAMPO NOME": funcionario['nome'],
                "CAMPO ANO": str(ano),
                "CAMPO HORARIO": str(funcionario.get('horario', '')),
                "CAMPO ENTRADA": str(funcionario.get('horarioentrada', '')),
                "CAMPO SAÍDA": str(funcionario.get('horariosaida', '')),
                "CAMPO MATRÍCULA": str(funcionario.get('matricula', '')),
                "CAMPO CARGO": funcionario.get('cargo', ''),
                "CAMPO FUNÇÃO": str(funcionario.get('funcao', '')),
            }

            for placeholder, valor in troca_de_dados.items():
                muda_texto_documento(doc, placeholder, valor)
            nome_limpo = funcionario['nome'].strip()
            setor_limpo = funcionario['setor'].strip()
            caminho_pasta = f"setor/{setor_limpo}/servidor/{mes_por_extenso}/{nome_limpo}"
            os.makedirs(caminho_pasta, exist_ok=True)

            nome_base = f"{nome_limpo.replace(' ', '_')}_FREQUENCIA"
            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)



             # Cria um arquivo ZIP com todos os PDFs
            zip_path = f"setor/frequencias_{mes_por_extenso}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))

            # Salva no banco o caminho do PDF
            #cursor.execute(
                #"INSERT INTO arquivos_zip (servidor_id, caminho_pdf) VALUES (%s, %s)",
                #(funcionario['id'], pdf_path)
            #)

        # Salva o ZIP no banco
        cursor.execute(
            "INSERT INTO arquivos_zip (mes, caminho_zip,tipo) VALUES (%s, %s,%s)",
            (mes_por_extenso, zip_path,'servidores')
        )

        conexao.commit()
        conexao.close()

        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'frequencias_servidores_{mes_por_extenso}.zip'
        )

    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro: {str(exception)}'}), 500


def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, funcionario):
    from datetime import date

    linha_inicial = 8  # Ajuste conforme necessário

    for table in doc.tables:
        # Configurar linhas existentes
        for row in table.rows:
            row.height = Cm(0.5)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    for run in paragraph.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(7)
                        run.font.bold = False

        # Validação de linhas
        if len(table.rows) < linha_inicial + quantidade_dias_no_mes:
            # Adiciona linhas extras se necessário
            for _ in range(linha_inicial + quantidade_dias_no_mes - len(table.rows)):
                new_row = table.add_row()
                for cell in new_row.cells:
                    cell.width = Cm(1.5)
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Preenchimento dos dias
        for i in range(quantidade_dias_no_mes):
            dia = i + 1
            dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
            row = table.rows[linha_inicial + i]
            
            # Limpa células antes de preencher
            for cell in row.cells:
                cell.text = ""
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    paragraph.clear()
            
            # Preenche dia
            dia_cell = row.cells[0]
            dia_paragraph = dia_cell.paragraphs[0]
            dia_run = dia_paragraph.add_run(str(dia))
            dia_run.font.name = "Calibri"
            dia_run.font.size = Pt(8)
            dia_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Verifica fins de semana
            if dia_semana == 5:    # Sábado
                texto = "SÁBADO"
                for j in [2, 5, 9, 13]:  # Células para marcar sábado
                    cell = row.cells[j]
                    cell.text = texto
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            elif dia_semana == 6:   # Domingo
                texto = "DOMINGO"
                for j in [2, 5, 9, 13]:  # Células para marcar domingo
                    cell = row.cells[j]
                    cell.text = texto
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        
            # Verifica férias
            if funcionario.get('feriasinicio') and funcionario.get('feriasfinal'):
                ferias_inicio = funcionario['feriasinicio'].date() if hasattr(funcionario['feriasinicio'], 'date') else funcionario['feriasinicio']
                ferias_final = funcionario['feriasfinal'].date() if hasattr(funcionario['feriasfinal'], 'date') else funcionario['feriasfinal']
                data_atual = date(ano, mes_numerico, dia)

                if ferias_inicio <= data_atual <= ferias_final and dia_semana not in [5, 6]:
                    texto = "FÉRIAS"
                    for j in [2, 5, 9, 13]:  # Células para marcar férias
                        cell = row.cells[j]
                        cell.text = texto
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True
                            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER