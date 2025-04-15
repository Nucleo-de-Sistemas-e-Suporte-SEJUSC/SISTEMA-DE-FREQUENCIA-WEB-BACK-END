from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import date, datetime, timedelta
from docx.shared import Pt,Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ROW_HEIGHT_RULE
import os
import zipfile 

bp_converte_estagiario_pdf = Blueprint('bp_converte_estagiario_pdf', __name__)

@bp_converte_estagiario_pdf.route('/api/estagiario/pdf', methods=['POST'])
def converte_estagiario_pdf():
    try:
        body = request.json or {}
        estagiarios_id = body.get('estagiarios', [])
        print(estagiarios_id)

        if not estagiarios_id:
            return jsonify({'erro': 'Nenhum estagiário selecionado'}), 400

        try:
            ids = [int(id) for id in estagiarios_id]
        except ValueError:
            return jsonify({'erro': 'IDs inválidos'}), 400

        mes_body = body.get('mes')
        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ','.join(['%s'] * len(ids))
        query = f"SELECT * FROM estagiarios WHERE id IN ({placeholders})"
        cursor.execute(query, ids)
        estagiarios = cursor.fetchall()


        if not estagiarios:
            conexao.close()
            return jsonify({'erro': 'Nenhum estagiário encontrado'}), 404

        arquivos_gerados = []

        for estagiario in estagiarios:
            template_path = 'FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx'
            doc = Document(template_path)

            cria_dias_da_celula(doc, ano, mes_numerico, estagiario)

            troca_de_dados = {
                "CAMPO SETOR": estagiario['setor'],
                "CAMPO MÊS": mes_por_extenso,
                "CAMPO NOME": estagiario['nome'],
                "CAMPO PERIODO": f"21/{mes_numerico}/{ano} a 20/{(mes_numerico % 12) + 1}/{ano if mes_numerico < 12 else ano + 1}",
                "CAMPO ANO": str(ano),
                "CAMPO HORARIO": str(estagiario.get('horario')),
                "CAMPO ENTRADA": str(estagiario.get('horario_entrada')),
                "CAMPO SAÍDA": str(estagiario.get('horario_saida')),
                "CAMPO CARGO": str(estagiario.get('cargo')),
            }

            for placeholder, valor in troca_de_dados.items():
                muda_texto_documento(doc, placeholder, valor)
            nome_limpo = estagiario['nome'].strip()
            setor_limpo = estagiario['setor'].strip()
            caminho_pasta = f"setor/{setor_limpo}/estagiario/{mes_por_extenso}/{nome_limpo}"
            os.makedirs(caminho_pasta, exist_ok=True)

            nome_base = f"{nome_limpo.replace(' ', '_')}_{estagiario['id']}_FREQUENCIA"
            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))


            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)

            # Salva no banco o caminho do PDF
            cursor.execute(
                "INSERT INTO arquivos_pdf (servidor_id, caminho_pdf) VALUES (%s, %s)",
                (estagiario['id'], pdf_path)
            )

        # Cria um arquivo ZIP com todos os PDFs
        zip_path = f"setor/frequencias_{mes_por_extenso}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))

        # Salva o ZIP no banco
        cursor.execute(
            "INSERT INTO arquivos_zip (mes, caminho_zip) VALUES (%s, %s)",
            (mes_por_extenso, zip_path)
        )

        conexao.commit()
        conexao.close()

        print(" TO CHEGANDO NO FINAL")

        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'frequencias_estagiarios_{mes_por_extenso}.zip'
        )

    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro: {str(exception)}'}), 500
    
    
def cria_dias_da_celula(doc, ano, mes_numerico, estagiario):
    from datetime import datetime, timedelta, date

    def calcula_periodo_21_a_20(ano, mes):
        """
        Calcula o intervalo de datas do dia 21 do mês atual ao dia 20 do próximo mês.
        Retorna uma lista de dicionários contendo os dias e os respectivos meses.
        """
        data_inicio = datetime(ano, mes, 21)
        if mes == 12:  # Caso especial para dezembro
            data_fim = datetime(ano + 1, 1, 20)
        else:
            data_fim = datetime(ano, mes + 1, 20)

        dias_periodo = []
        data_atual = data_inicio
        while data_atual <= data_fim:
            dias_periodo.append({
                "dia": data_atual.day,
                "mes": data_atual.month,
                "ano": data_atual.year
            })
            data_atual += timedelta(days=1)
        
        return dias_periodo

    linha_inicial = 8  # Ajuste conforme seu template

    for table in doc.tables:
        table.autofit = False
        
        for row in table.rows:
            row.height = Cm(0.5)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in row.cells:
                cell.width = Cm(1.5)
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    for run in paragraph.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(9)

        dias_periodo = calcula_periodo_21_a_20(ano, mes_numerico)
        linhas_necessarias = linha_inicial + len(dias_periodo)

        # Validação: impede execução se faltar linha
        if len(table.rows) < linhas_necessarias:
            raise Exception(
                f"O template possui {len(table.rows)} linhas, mas são necessárias {linhas_necessarias} "
                f"para preencher o período de 21/{mes_numerico}/{ano} a 20/{(mes_numerico % 12) + 1}/{ano if mes_numerico < 12 else ano + 1}."
            )

        # Só executa se houver linhas suficientes
        for i, dia_info in enumerate(dias_periodo):
            dia = dia_info["dia"]
            mes = dia_info["mes"]
            ano_dia = dia_info["ano"]

            dia_semana = pega_final_de_semana(ano_dia, mes, dia)
            row = table.rows[linha_inicial + i]
            dia_cell = row.cells[0]
            dia_cell.text = str(dia)

            if dia_semana == 5:    # Sábado
                for j in [2, 5, 9, 13]:
                    cell = row.cells[j]
                    cell.text = "SÁBADO"
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            elif dia_semana == 6:   # Domingo
                for j in [2, 5, 9, 13]:
                    cell = row.cells[j]
                    cell.text = "DOMINGO"
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            if estagiario.get('feriasinicio') and estagiario.get('feriasfinal'):
                ferias_inicio = estagiario['feriasinicio'].date() if hasattr(estagiario['feriasinicio'], 'date') else estagiario['feriasinicio']
                ferias_final = estagiario['feriasfinal'].date() if hasattr(estagiario['feriasfinal'], 'date') else estagiario['feriasfinal']
                data_atual = date(ano_dia, mes, dia)
                if ferias_inicio <= data_atual <= ferias_final and dia_semana not in [5, 6]:
                    for j in [2, 5, 9, 13]:
                        cell = row.cells[j]
                        cell.text = "FÉRIAS"
                        for paragraph in cell.paragraphs:
                            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER