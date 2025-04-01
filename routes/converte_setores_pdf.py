from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from docx import Document
from datetime import datetime, date
import os
from flask_login import login_required
from decorador import roles_required
from flask import send_file
import shutil

bp_converte_setor_pdf = Blueprint('bp_converte_setor_pdf', __name__)

@bp_converte_setor_pdf.route('/api/setores/pdf', methods=['POST'])
def converte_setores_pdf():
    try:
        body = request.json or {}
        setores_nomes = body.get('setores', [])

        if not setores_nomes:
            return jsonify({'erro': 'Nenhum setor selecionado'}), 400

        if not all(isinstance(nome, str) and nome.strip() for nome in setores_nomes):
            return jsonify({'erro': 'Nomes de setores inválidos'}), 400

        mes_body = body.get('mes')
        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ','.join(['%s'] * len(setores_nomes))
        query_funcionarios = f"""
            SELECT * FROM funcionarios 
            WHERE setor IN ({placeholders})
            ORDER BY setor, nome
        """
        cursor.execute(query_funcionarios, setores_nomes)
        servidores = cursor.fetchall()

        if not servidores:
            conexao.close()
            return jsonify({
                'erro': 'Nenhum servidor encontrado nos setores selecionados',
                'setores_procurados': setores_nomes
            }), 404

        resultados = []

        # Cria uma pasta temporária para armazenar os documentos gerados
        pasta_temp = f"temp/{mes_por_extenso}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.makedirs(pasta_temp, exist_ok=True)

        for servidor in servidores:
            try:
                # Processa cada servidor
                template_path = 'FREQUÊNCIA_MENSAL.docx'
                doc = Document(template_path)

                # Preenche os dias do mês
                for table in doc.tables:
                    if len(table.rows) >= 8 + quantidade_dias_no_mes:
                        for i in range(quantidade_dias_no_mes):
                            dia = i + 1
                            dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
                            row = table.rows[8 + i]
                            row.cells[0].text = str(dia)

                            if dia_semana == 5:  # Sábado
                                row.cells[2].text = "SÁBADO"
                                row.cells[5].text = "SÁBADO"
                                row.cells[9].text = "SÁBADO"
                                row.cells[13].text = "SÁBADO"
                            elif dia_semana == 6:  # Domingo
                                row.cells[2].text = "DOMINGO"
                                row.cells[5].text = "DOMINGO"
                                row.cells[9].text = "DOMINGO"
                                row.cells[13].text = "DOMINGO"

                            # Verifica férias
                            if servidor['feriasinicio'] and servidor['feriasfinal']:
                                data_dia = date(ano, mes_numerico, dia)
                                if servidor['feriasinicio'] <= data_dia <= servidor['feriasfinal'] and dia_semana not in [5, 6]:
                                    row.cells[2].text = "FÉRIAS"
                                    row.cells[5].text = "FÉRIAS"
                                    row.cells[9].text = "FÉRIAS"
                                    row.cells[13].text = "FÉRIAS"

                # Substitui os placeholders
                troca_de_dados = {
                    "CAMPO SETOR": servidor['setor'],
                    "CAMPO MÊS": mes_por_extenso,
                    "CAMPO NOME": servidor['nome'],
                    "CAMPO ANO": str(ano),
                    "CAMPO HORARIO": str(servidor['horario']),
                    "CAMPO ENTRADA": str(servidor['horarioentrada']),
                    "CAMPO SAÍDA": str(servidor['horariosaida']),
                    "CAMPO MATRÍCULA": str(servidor['matricula']),
                    "CAMPO CARGO": servidor['cargo'],
                    "CAMPO FUNÇÃO": str(servidor['funcao']),
                }

                for placeholder, valor in troca_de_dados.items():
                    muda_texto_documento(doc, placeholder, valor)

                # Gera os arquivos
                nome_base = f"{servidor['nome']}_FREQUÊNCIA_MENSAL"
                docx_path = os.path.join(pasta_temp, f"{nome_base}.docx")
                pdf_path = os.path.join(pasta_temp, f"{nome_base}.pdf")
                doc.save(docx_path)
                convert_to_pdf(docx_path, pdf_path)

                resultados.append({
                    'nome': servidor['nome'],
                    'matricula': servidor['matricula'],
                    'setor': servidor['setor'],
                    'documento': f"{nome_base}.pdf",
                    'caminho': pdf_path
                })

            except Exception as e:
                resultados.append({
                    'nome': servidor.get('nome', 'Desconhecido'),
                    'setor': servidor.get('setor', 'Desconhecido'),
                    'erro': str(e)
                })

        conexao.close()

        # Compacta todos os PDFs em um único arquivo ZIP
        zip_path = f"{pasta_temp}.zip"
        shutil.make_archive(pasta_temp, 'zip', pasta_temp)

        # Retorna o arquivo ZIP para download
        return send_file(zip_path, as_attachment=True, download_name=f"setores_{mes_por_extenso}.zip")

    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro no servidor: {str(exception)}'}), 500
