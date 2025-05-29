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
from datetime import datetime, date,time,timedelta
import uuid

bp_converte_setor_pdf = Blueprint('bp_converte_setor_pdf', __name__)




def formatar_horario_para_hh_mm_v2(valor_horario):
    """
    Formata um valor de horário para o formato HH:MM, removendo os segundos.
    """
    if not valor_horario:  # Se for None, string vazia, etc.
        return ''

    # Caso 1: Se for um objeto datetime.time
    if isinstance(valor_horario, time):
        return valor_horario.strftime('%H:%M')

    # Caso 2: Se for um objeto datetime.timedelta (comum de bancos de dados para colunas TIME)
    if isinstance(valor_horario, timedelta):
        total_seconds = int(valor_horario.total_seconds())
        # Ignora dias, foca apenas na parte de tempo do dia
        if total_seconds < 0: # Lida com timedeltas negativos, se aplicável
            # Você pode querer um tratamento específico aqui, por ex., '' ou erro
            # Para simplificar, vamos assumir horas e minutos a partir de 0 se for negativo
            # ou tratar como 00:00. A lógica exata pode depender do seu caso de uso.
            # Exemplo: tratar como 00:00 se negativo ou converter para positivo
            # Para este exemplo, vamos apenas calcular com base no valor absoluto.
            total_seconds = abs(total_seconds)

        hours = (total_seconds // 3600) % 24 # Garante que as horas fiquem dentro de 0-23
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"

    # Caso 3: Se for uma string
    if isinstance(valor_horario, str):
        try:
            # Tenta primeiro como HH:MM:SS
            if valor_horario.count(':') == 2:
                dt_obj = datetime.strptime(valor_horario, '%H:%M:%S')
                return dt_obj.strftime('%H:%M')
            # Depois como HH:MM
            elif valor_horario.count(':') == 1:
                dt_obj = datetime.strptime(valor_horario, '%H:%M')
                return dt_obj.strftime('%H:%M') # Já está no formato, mas re-formata para garantir
            else:
                # Se não for um formato de tempo reconhecido, retorna a string original
                return valor_horario
        except ValueError:
            # Se a conversão da string falhar
            return valor_horario # Retorna a string original

    # Fallback: Se não for nenhum dos tipos acima, tenta converter para string
    return str(valor_horario)

@bp_converte_setor_pdf.route('/api/setores/pdf', methods=['POST'])
def converte_setores_pdf():
    try:
        body = request.json or {}
        setores = body.get('setores')  # Agora aceita lista de setores
        mes_body = body.get('mes')

        if not setores or not isinstance(setores, list):
            return jsonify({'erro': 'Nenhum setor selecionado ou formato inválido'}), 400

        arquivos_zip_gerados = []
        mes_por_extenso = data_atual(mes_body)['mes']

        for setor_nome in setores:
            data_ano_mes_atual = data_atual(mes_body)
            mes_numerico = data_ano_mes_atual['mes_numerico']
            ano = data_ano_mes_atual['ano']
            quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico) 

            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)

            # Busca todos os funcionários do setor especificado
            query = "SELECT * FROM funcionarios WHERE setor = %s"
            cursor.execute(query, (setor_nome,))
            funcionarios = cursor.fetchall()

            if not funcionarios:
                conexao.close()
                continue  # Pula para o próximo setor

            arquivos_gerados = []
            setor_limpo = setor_nome.strip().replace('/', '_')

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
                    "CAMPO ENTRADA": formatar_horario_para_hh_mm_v2(funcionario.get('horarioentrada', '')),
                    "CAMPO SAÍDA": formatar_horario_para_hh_mm_v2(funcionario.get('horariosaida', '')),
                    "CAMPO MATRÍCULA": str(funcionario.get('matricula', '')),
                    "CAMPO CARGO": funcionario.get('cargo', ''),
                }

                for placeholder, valor in troca_de_dados.items():
                    muda_texto_documento(doc, placeholder, valor)

                nome_limpo = funcionario['nome'].strip().replace('/', '_')
                caminho_pasta = f"setor/{setor_limpo}/{mes_por_extenso}"
                os.makedirs(caminho_pasta, exist_ok=True)

                nome_base = f"FREQUENCIA_{nome_limpo.replace(' ', '_')}"
                docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
                pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

                doc.save(docx_path)
                convert_to_pdf(docx_path, pdf_path)
                arquivos_gerados.append(pdf_path)

                cursor.execute(
                    "INSERT INTO arquivos_pdf (servidor_id, caminho_pdf) VALUES (%s, %s)",
                    (funcionario['id'], pdf_path)
                )

            # Cria arquivo ZIP com todos os PDFs do setor
            zip_path = f"setor/{setor_limpo}/frequencias_{setor_limpo}_{mes_por_extenso}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for pdf in arquivos_gerados:
                    zipf.write(pdf, os.path.basename(pdf))

            # Salva o ZIP do setor no banco
            cursor.execute(
                "INSERT INTO arquivos_zip (setor, mes, caminho_zip, tipo) VALUES (%s, %s, %s, %s)",
                (setor_nome, mes_por_extenso, zip_path, 'funcionarios')
            )

            conexao.commit()
            conexao.close()

            arquivos_zip_gerados.append(zip_path)

        # Se mais de um setor, cria um ZIP final com todos os ZIPs dos setores e salva no banco
        if len(arquivos_zip_gerados) > 1:
            zip_final_path = f"setor/frequencias_multissetores_{mes_body}.zip"
            with zipfile.ZipFile(zip_final_path, 'w') as zipf:
                for zip_file in arquivos_zip_gerados:
                    zipf.write(zip_file, os.path.basename(zip_file))
            # Salva o ZIP de multissetores no banco
            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO arquivos_zip (setor, mes, caminho_zip, tipo) VALUES (%s, %s, %s, %s)",
                ('multissetores', mes_por_extenso, zip_final_path, 'multissetores')
            )
            conexao.commit()
            conexao.close()
            return send_file(zip_final_path, mimetype='application/zip', as_attachment=True)
        elif arquivos_zip_gerados:
            return send_file(arquivos_zip_gerados[0], mimetype='application/zip', as_attachment=True)
        else:
            return jsonify({'erro': 'Nenhum setor válido foi processado'}), 404

    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro ao processar setores: {str(exception)}'}), 500



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