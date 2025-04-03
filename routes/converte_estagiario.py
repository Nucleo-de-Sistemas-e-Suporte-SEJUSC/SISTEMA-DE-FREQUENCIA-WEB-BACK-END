from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import date, datetime, timedelta
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

bp_converte_estagiario_pdf = Blueprint('bp_converte_estagiario_pdf', __name__)

@bp_converte_estagiario_pdf.route('/api/estagiario/pdf', methods=['POST'])
def converte_estagiario_pdf():
    try:
        body = request.json or {}
        estagiarios_id = body.get('estagiarios', [])
        
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
        estagiarioes = cursor.fetchall()

        if not estagiarioes:
            conexao.close()
            return jsonify({'erro': 'Nenhum estagiário encontrado'}), 404

        template_path = 'FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx'
        
        # Processa apenas o primeiro estagiário (ou ajuste para múltiplos arquivos)
        estagiario = estagiarioes[0]
        
        doc = Document(template_path)
        
        # Ajuste aqui para usar o período correto
        cria_dias_da_celula(doc, ano, mes_numerico, estagiario)

        troca_de_dados = {
            "CAMPO SETOR": estagiario['setor'],  # Substituído 'setor' por 'lotacao'
            "CAMPO MÊS": mes_por_extenso,
            "CAMPO NOME": estagiario['nome'],
            "CAMPO PERIODO": f"21/{mes_numerico}/{ano} a 20/{(mes_numerico % 12) + 1}/{ano if mes_numerico < 12 else ano + 1}",
            "CAMPO ANO": str(ano),
            "CAMPO HORARIO": str(estagiario['horario']),
            "CAMPO ENTRADA": str(estagiario.get('horario_entrada')),  # Ajuste conforme necessário
            "CAMPO SAÍDA": str(estagiario.get('horario_saida')),      # Ajuste conforme necessário
        }

        for placeholder, valor in troca_de_dados.items():
            muda_texto_documento(doc, placeholder, valor)

        caminho_pasta = f"setor/{estagiario['setor']}/estagiario/{mes_por_extenso}/{estagiario['nome']}"
        os.makedirs(caminho_pasta, exist_ok=True)

        nome_base = f"{estagiario['nome']}FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx"
        docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
        pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

        doc.save(docx_path)
        convert_to_pdf(docx_path, pdf_path)

        conexao.close()

        return send_file(pdf_path, as_attachment=True, download_name=f"{nome_base}.pdf")
    
    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro no estagiário: {str(exception)}'}), 500

    
    
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


def cria_dias_da_celula(doc, ano, mes_numerico, estagiario):
    linha_inicial = 8  # Linha inicial onde começa o preenchimento dos dias
    dias_periodo = calcula_periodo_21_a_20(ano, mes_numerico)

    def formatar_celula(celula, texto):
        """
        Formata a célula com o texto especificado e ajusta alinhamento e estilo.
        """
        # Limpa qualquer conteúdo anterior na célula
        celula.text = ""
        
        # Adiciona o texto formatado
        p = celula.add_paragraph(texto)
        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Centraliza horizontalmente
        run = p.runs[0]
        run.font.size = Pt(10)  # Define tamanho da fonte

    for table in doc.tables:
        for i, dia_info in enumerate(dias_periodo):
            dia = dia_info['dia']
            mes = dia_info['mes']
            ano = dia_info['ano']
            dia_semana = pega_final_de_semana(ano, mes, dia)

            row = table.rows[linha_inicial + i]

            if dia_semana == 5:  # Sábado
                formatar_celula(row.cells[1], "SÁBADO")
                formatar_celula(row.cells[2], "SÁBADO")
                formatar_celula(row.cells[4], "SÁBADO")
                formatar_celula(row.cells[5], "SÁBADO")

            if dia_semana == 6:  # Domingo
                formatar_celula(row.cells[1], "DOMINGO")
                formatar_celula(row.cells[2], "DOMINGO")
                formatar_celula(row.cells[4], "DOMINGO")
                formatar_celula(row.cells[5], "DOMINGO")

