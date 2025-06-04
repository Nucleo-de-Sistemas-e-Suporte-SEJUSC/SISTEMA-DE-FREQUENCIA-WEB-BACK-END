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
import holidays
from datetime import datetime, date, timedelta,time
import zipfile
import re
from datetime import date
from dateutil.easter import easter


bp_converte_servidor_pdf = Blueprint('bp_converte_servidor_pdf', __name__)

def pegar_feriados_mes(ano, mes, estado='AM'):
    br_feriados = holidays.Brazil(state=estado)
    pascoa = easter(ano)
    corpus_christi = pascoa + timedelta(days=60)
    br_feriados[corpus_christi] = "Corpus Christi"

    # Busca feriados municipais do banco pelo estado
    conexao = connect_mysql()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        "SELECT data FROM feriados_municipais WHERE estado = %s AND YEAR(data) = %s",
        (estado, ano)
    )
    feriados_municipais = [row['data'] for row in cursor.fetchall()]
    conexao.close()
    for data_str in feriados_municipais:
        data_feriado = date.fromisoformat(str(data_str))
        br_feriados[data_feriado] = "Feriado Municipal"

    feriados_mes = [d for d in br_feriados if d.month == mes]
    return feriados_mes

def limpa_nome(nome):
    return re.sub(r'[^\w\s-]', '', nome).strip().replace(' ', '_')


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

@bp_converte_servidor_pdf.route('/api/servidores/pdf', methods=['POST'])
def converte_servidor_pdf():
    try:
        body = request.json or {}
        funcionarios_id = body.get('funcionarios', [])

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
            estado_funcionarios = funcionarios.get('estado', 'AM')  # Padrão para AM, pode ser ajustado conforme necessário
            feriados_do_mes = pegar_feriados_mes(ano, mes_numerico,estado=estado_funcionarios)
            template_path = 'FREQUÊNCIA_MENSAL.docx'
            doc = Document(template_path)

            cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, funcionario, feriados_do_mes)
            # Formatar horário
            troca_de_dados = {
            "CAMPO SETOR": funcionario['setor'],
            "CAMPO MÊS": mes_por_extenso,
            "CAMPO NOME": funcionario['nome'],
            "CAMPO ANO": str(ano),
            "CAMPO HORARIO": funcionario.get('horario', ''), # Mantido como está, sem formatação específica aqui
            "CAMPO ENTRADA": formatar_horario_para_hh_mm_v2(funcionario.get('horarioentrada', '')),
            "CAMPO SAÍDA": formatar_horario_para_hh_mm_v2(funcionario.get('horariosaida', '')),
            "CAMPO MATRÍCULA": str(funcionario.get('matricula', '')),
            "CAMPO CARGO": funcionario.get('cargo', ''),
        }

            for placeholder, valor in troca_de_dados.items():
                muda_texto_documento(doc, placeholder, valor)

            nome_limpo = limpa_nome(funcionario['nome'])
            setor_limpo = limpa_nome(funcionario['setor'])
            caminho_pasta = f"setor/{setor_limpo}/servidor/{mes_por_extenso}/{nome_limpo}"
            os.makedirs(caminho_pasta, exist_ok=True)

            nome_base = f"{nome_limpo}_FREQUENCIA"
            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)

        # Criar ZIP com todos os PDFs
        zip_path = os.path.abspath(f"setor/frequencias_{mes_por_extenso}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))

        # Salvar caminho do ZIP no banco
        cursor.execute(
            "INSERT INTO arquivos_zip (mes, caminho_zip, tipo) VALUES (%s, %s, %s)",
            (mes_por_extenso, zip_path, 'servidores')
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

def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, funcionario, feriados):
    linha_inicial = 8

    for table in doc.tables:
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

        if len(table.rows) < linha_inicial + quantidade_dias_no_mes:
            for _ in range(linha_inicial + quantidade_dias_no_mes - len(table.rows)):
                new_row = table.add_row()
                for cell in new_row.cells:
                    cell.width = Cm(1.5)
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        for i in range(quantidade_dias_no_mes):
            dia = i + 1
            dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
            data_atual = date(ano, mes_numerico, dia)
            row = table.rows[linha_inicial + i]

            for cell in row.cells:
                cell.text = ""
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    paragraph.clear()

            # Preencher número do dia
            dia_cell = row.cells[0]
            dia_paragraph = dia_cell.paragraphs[0]
            dia_run = dia_paragraph.add_run(str(dia))
            dia_run.font.name = "Calibri"
            dia_run.font.size = Pt(8)
            dia_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Sábados e Domingos
            if dia_semana == 5:
                texto = "SÁBADO"
            elif dia_semana == 6:
                texto = "DOMINGO"
            else:
                texto = ""

            if texto:
                for j in [2, 5, 9, 13]:
                    cell = row.cells[j]
                    cell.text = texto
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Feriado (exceto se for sábado ou domingo)
            if data_atual in feriados and dia_semana not in [5, 6]:
                for j in [2, 5, 9, 13]:
                    cell = row.cells[j]
                    cell.text = "FERIADO"
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Férias (exceto fins de semana)
            if funcionario.get('feriasinicio') and funcionario.get('feriasfinal'):
                ferias_inicio = funcionario['feriasinicio'].date() if hasattr(funcionario['feriasinicio'], 'date') else funcionario['feriasinicio']
                ferias_final = funcionario['feriasfinal'].date() if hasattr(funcionario['feriasfinal'], 'date') else funcionario['feriasfinal']
                if ferias_inicio <= data_atual <= ferias_final and dia_semana not in [5, 6]:
                    for j in [2, 5, 9, 13]:
                        cell = row.cells[j]
                        cell.text = "FÉRIAS"
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True
                            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
