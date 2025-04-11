from utils.convert_to_pdf import convert_to_pdf
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import datetime, date
from docx.shared import Pt, Cm
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT  # Importa alinhamento de parágrafo
import os
import zipfile

bp_converte_setor_pdf = Blueprint('bp_converte_setor_pdf', __name__)

@bp_converte_setor_pdf.route('/api/setores/pdf', methods=['POST'])
def converte_setores_pf():
    try:
        # Verifica se o corpo da requisição está presente e é válido
        body = request.json or {}
        if not body:
            return jsonify({'erro': 'O corpo da requisição está vazio ou inválido'}), 400

        # Recupera os dados do corpo da requisição
        setor = body.get('setor')
        mes_body = body.get('mes', None)

        # Valida se o setor foi informado
        if not setor:
            return jsonify({'erro': 'O campo "setor" é obrigatório'}), 400

        # Conexão com o banco de dados MySQL
        conexao = connect_mysql()
        if not conexao:
            return jsonify({'erro': 'Falha ao conectar ao banco de dados'}), 500

        cursor = conexao.cursor(dictionary=True)

        # Processa a data informada ou usa a data atual
        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']
            
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        template_path = 'FREQUÊNCIA_MENSAL.docx'

        # Consulta funcionários do setor informado
        busca_setor = "SELECT * FROM funcionarios WHERE setor = %s"
        cursor.execute(busca_setor, (setor,))
        funcionarios = cursor.fetchall()

        if len(funcionarios) == 0:
            conexao.close()
            return jsonify({'erro': 'Setor não encontrado ou sem funcionários'}), 404

        arquivos_gerados = []

        for funcionario in funcionarios:
            caminho_pasta = f"setor/{funcionario['setor']}/servidor/{mes_por_extenso}/{funcionario['nome']}"
            os.makedirs(caminho_pasta, exist_ok=True)

            docx_path = os.path.join(caminho_pasta, f"{funcionario['nome']}_FREQUÊNCIA_MENSAL.docx")
            pdf_path = os.path.join(caminho_pasta, f"{funcionario['nome']}_FREQUÊNCIA_MENSAL.pdf")

            # Criação do documento Word baseado no template
            doc = Document(template_path)

            # Substitui os placeholders pelos valores reais
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

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for placeholder, valor in troca_de_dados.items():
                                if placeholder in paragraph.text:
                                    paragraph.text = paragraph.text.replace(placeholder, valor)

            linha_inicial = 9

            for table in doc.tables:
                table.autofit = False
                
                for row in table.rows:
                    row.height = Cm(0.5)
                    row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
                    
                    for cell in row.cells:
                        cell.width = Cm(1.5)
                        
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.name = "Calibri"
                                run.font.size = Pt(9)

                if len(table.rows) >= linha_inicial + quantidade_dias_no_mes:
                    for i in range(quantidade_dias_no_mes):
                        dia_cell = table.rows[linha_inicial + i].cells[0]
                        dia_cell.text = str(i + 1)

                        dia_semana = pega_final_de_semana(ano, mes_numerico, i + 1)
                        
                        if dia_semana == 5:  # Sábado
                            for j in [2, 5, 9, 13]:
                                cell = table.rows[linha_inicial + i].cells[j]
                                cell.text = "SÁBADO"
                        elif dia_semana == 6:  # Domingo
                            for j in [2, 5, 9, 13]:
                                cell = table.rows[linha_inicial + i].cells[j]
                                cell.text = "DOMINGO"

                        ferias_inicio = funcionario.get('feriasinicio')
                        ferias_final = funcionario.get('feriasfinal')

                        if ferias_inicio and ferias_final:
                            if isinstance(ferias_inicio, datetime):
                                ferias_inicio = ferias_inicio.date()
                            if isinstance(ferias_final, datetime):
                                ferias_final = ferias_final.date()
                            
                            dia_atual = date(ano, mes_numerico, i + 1)
                            if ferias_inicio <= dia_atual <= ferias_final and dia_semana not in [5, 6]:
                                for j in [2, 5, 9, 13]:
                                    cell.text = "FÉRIAS"

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)
            
        # Cria um arquivo ZIP contendo todos os PDFs gerados
        zip_path = f"setor/{setor}_{mes_por_extenso}_frequencia_mensal.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))  # Adiciona o PDF ao ZIP

        cursor.execute(
            "INSERT INTO arquivos_zip (mes, setor, caminho_zip) VALUES (%s, %s, %s)",
            (mes_por_extenso, setor, zip_path)
        )
        conexao.commit()
        conexao.close()

        conexao.close()

        return jsonify({'mensagem': 'Documentos gerados com sucesso!', 'zip_path': zip_path})
        
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500

