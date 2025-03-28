from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import datetime, date
import os
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 
 # Importa o decorador personalizado


bp_converte_servidor_pdf = Blueprint('bp_converte_servidor_pdf', __name__)

@bp_converte_servidor_pdf.route('/api/servidores/pdf', methods=['POST'])
# @login_required
# @roles_required('admin','editor')
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
        print(data_ano_mes_atual)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ','.join(['%s'] * len(ids))
        query = f"SELECT * FROM funcionarios WHERE id IN ({placeholders})"
        cursor.execute(query, ids)
        servidores = cursor.fetchall()

        if not servidores:
            conexao.close()
            return jsonify({'erro': 'Nenhum servidor encontrado'}), 404

        resultados = []
        template_path = 'FREQUÊNCIA_MENSAL.docx'

        for servidor in servidores:
            try:
                doc = Document(template_path)
                cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, servidor)

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

                caminho_pasta = f"setor/{servidor['setor']}/servidor/{mes_por_extenso}/{servidor['nome']}"
                os.makedirs(caminho_pasta, exist_ok=True)

                nome_base = f"{servidor['nome']}_FREQUÊNCIA_MENSAL"
                docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
                pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

                doc.save(docx_path)
                convert_to_pdf(docx_path, pdf_path)

                resultados.append({
                    'nome': servidor['nome'],
                    'matricula': servidor['matricula'],
                    'documento': f"{nome_base}.pdf",
                    'caminho': pdf_path
                })

            except Exception as e:
                resultados.append({
                    'nome': servidor.get('nome', 'Desconhecido'),
                    'erro': str(e)
                })

        conexao.close()
        return jsonify({
            'mensagem': 'Processamento concluído',
            'resultados': resultados,
            'total_processados': len(servidores),
            'sucessos': len([r for r in resultados if 'erro' not in r])
        }), 200

    except Exception as exception:
        if 'conexao' in locals():
            conexao.close()
        return jsonify({'erro': f'Erro no servidor: {str(exception)}'}), 500

def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, servidor):
    linha_inicial = 8

    for table in doc.tables:
        if len(table.rows) >= linha_inicial + quantidade_dias_no_mes:
            for i in range(quantidade_dias_no_mes):
                dia = i + 1
                dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
                row = table.rows[linha_inicial + i] 
                dia_cell = row.cells[0] 
                dia_cell.text = str(dia)

                if dia_semana == 5:    
                    row.cells[2].text = "SÁBADO"
                    row.cells[5].text = "SÁBADO"
                    row.cells[9].text = "SÁBADO"
                    row.cells[13].text = "SÁBADO"
                elif dia_semana == 6:   
                    row.cells[2].text = "DOMINGO"
                    row.cells[5].text = "DOMINGO"
                    row.cells[9].text = "DOMINGO"
                    row.cells[13].text = "DOMINGO"

                if servidor['feriasinicio'] and servidor['feriasfinal']:
                    data_atual = date(ano, mes_numerico, dia)
                    if servidor['feriasinicio'] <= data_atual <= servidor['feriasfinal'] and dia_semana not in [5, 6]:
                        row.cells[2].text = "FÉRIAS"
                        row.cells[5].text = "FÉRIAS"
                        row.cells[9].text = "FÉRIAS"
                        row.cells[13].text = "FÉRIAS"
        else:
            print(f"A tabela não tem linhas suficientes para os {quantidade_dias_no_mes} dias do mês.")