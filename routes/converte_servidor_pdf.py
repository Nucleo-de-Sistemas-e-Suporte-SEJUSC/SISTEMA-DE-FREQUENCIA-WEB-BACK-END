from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import datetime, date
from docx.shared import Pt, Cm
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT # Importa alinhamento de parágrafo
import zipfile 
import os

bp_converte_servidor_pdf = Blueprint('bp_converte_servidor_pdf', __name__)

@bp_converte_servidor_pdf.route('/api/servidores/pdf', methods=['POST'])
def converte_servidor_pdf():
    try:
        body = request.json or {}
        funcionarios_id = body.get('funcionarios', [])
        mes_body = body.get('mes')

        if not funcionarios_id:
            return jsonify({'erro': 'Nenhum ID de funcionário fornecido'}), 400

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Busca todos os servidores de uma vez
        placeholders = ','.join(['%s'] * len(funcionarios_id))
        query = f"SELECT * FROM funcionarios WHERE id IN ({placeholders})"
        cursor.execute(query, funcionarios_id)
        servidores = cursor.fetchall()

        if not servidores:
            conexao.close()
            return jsonify({'erro': 'Nenhum servidor encontrado'}), 404

        # Processa informações do mês
        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        template_path = 'FREQUÊNCIA_MENSAL.docx'
        arquivos_gerados = []
        nomes_servidores = []

        # Gera PDFs para cada servidor
        for servidor in servidores:
            doc = Document(template_path)
            cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, servidor)

            troca_de_dados = {
                "CAMPO SETOR": servidor['setor'],
                "CAMPO MÊS": mes_por_extenso,
                "CAMPO NOME": servidor['nome'],
                "CAMPO ANO": str(ano),
                "CAMPO HORARIO": str(servidor.get('horario', '')),
                "CAMPO ENTRADA": str(servidor.get('horarioentrada', '')),
                "CAMPO SAÍDA": str(servidor.get('horariosaida', '')),
                "CAMPO MATRÍCULA": str(servidor.get('matricula', '')),
                "CAMPO CARGO": servidor.get('cargo', ''),
                "CAMPO FUNÇÃO": str(servidor.get('funcao', '')),
            }

            for placeholder, valor in troca_de_dados.items():
                muda_texto_documento(doc, placeholder, valor)
            
            caminho_pasta = f"setor/{servidor['setor']}/servidor/{mes_por_extenso}/{servidor['nome']}"
            os.makedirs(caminho_pasta, exist_ok=True)

            nome_base = f"{servidor['nome']}_FREQUÊNCIA_MENSAL"
            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)

            # Salva o caminho do PDF no banco de dados
            arquivos_gerados.append(pdf_path)
            nomes_servidores.append(servidor['nome'])
            
            cursor.execute(
                "INSERT INTO arquivos_pdf (servidor_id, caminho_pdf) VALUES (%s, %s)",
                (servidor['id'], pdf_path)
            )


        # Cria um arquivo ZIP contendo todos os PDFs gerados
       # Nome do ZIP com todos os servidores
        zip_path = f"setor/frequencias_{mes_por_extenso}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))

        # Salva no banco com os IDs relacionados
        cursor.execute(
            "INSERT INTO arquivos_zip (mes, caminho_zip, servidores_ids) VALUES (%s, %s, %s)",
            (mes_por_extenso, zip_path, ','.join(funcionarios_id))
        )
        
        conexao.commit()
        conexao.close()

        return jsonify({
            'mensagem': 'Documentos gerados com sucesso!',
            'zip_path': zip_path,
            'servidores': nomes_servidores
        })
    
    except Exception as e:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': str(e)}), 500

def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, servidor):
    linha_inicial = 8

    for table in doc.tables:
        table.autofit = False  # Desativa ajuste automático da tabela
        
        for row in table.rows:
            row.height = Cm(0.5)  # Define altura fixa das linhas para compactação
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            
            for cell in row.cells:
                cell.width = Cm(3.0)  # Define largura fixa das células
                
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Centraliza o texto nas células
                    for run in paragraph.runs:
                        run.font.name = "Calibri"  # Define fonte como Calibri
                        run.font.size = Pt(7)      # Define tamanho da fonte como 9 pontos

        if len(table.rows) >= linha_inicial + quantidade_dias_no_mes:
            for i in range(quantidade_dias_no_mes):
                dia = i + 1
                dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
                row = table.rows[linha_inicial + i]
                
                dia_cell = row.cells[0]
                dia_cell.text = str(dia)
                for paragraph in dia_cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

                if dia_semana == 5:    
                    for j in [2, 5, 9, 13]:
                        cell = row.cells[j]
                        cell.text = "SÁBADO"
                        for paragraph in cell.paragraphs:
                            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

                elif dia_semana == 6:   
                    for j in [2, 5, 9, 13]:
                        cell = row.cells[j]
                        cell.text = "DOMINGO"
                        for paragraph in cell.paragraphs:
                            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

                if servidor['feriasinicio'] and servidor['feriasfinal']:
                    ferias_inicio = servidor['feriasinicio'].date() if hasattr(servidor['feriasinicio'], 'date') else servidor['feriasinicio']
                    ferias_final = servidor['feriasfinal'].date() if hasattr(servidor['feriasfinal'], 'date') else servidor['feriasfinal']
                    
                    print("AQUI")
                    data_atual = date(ano, mes_numerico, dia)
                    if ferias_inicio <= data_atual <= ferias_final and dia_semana not in [5, 6]:
                        for j in [2, 5, 9, 13]:
                            cell = row.cells[j]
                            cell.text = "FÉRIAS"
                            for paragraph in cell.paragraphs:
                                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
