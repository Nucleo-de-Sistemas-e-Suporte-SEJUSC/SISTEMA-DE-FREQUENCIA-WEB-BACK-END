from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import datetime, date
import win32com.client
import pythoncom 
import os
import calendar

bp_converte_servidor_pdf = Blueprint('bp_converte_servidor_pdf', __name__)

@bp_converte_servidor_pdf.route('/api/servidores/pdf/<int:servidor_id>', methods=['POST'])
def converte_servidor_pdf(servidor_id):
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        body = request.json or {}

        
        if request.is_json:
            mes_body = body.get('mes', None)


        if mes_body is not None:
            data_ano_mes_atual = data_atual(mes_body)
            mes_por_extenso = data_ano_mes_atual['mes']
            mes_numerico = data_ano_mes_atual['mes_numerico']
        else: 
            print(mes_body)
            data_ano_mes_atual = data_atual(mes_informado_pelo_usuario=None)
            print(data_ano_mes_atual)
            mes_por_extenso = data_ano_mes_atual['mes'] 
            mes_numerico = data_ano_mes_atual['mes_numerico']
            

        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano,mes_numerico)

        template_path = 'FREQUÊNCIA_MENSAL.docx'
        doc = Document(template_path)

        busca_servidor_por_id = "SELECT * FROM funcionarios WHERE id = %s"
        cursor.execute(busca_servidor_por_id, (servidor_id,))
        servidor = cursor.fetchone()
        print(servidor)

        if not servidor:
            conexao.close()
            return jsonify({'erro': 'Servidor não encontrado'}), 404

        gera_dados_celula = cria_dias_da_celula(doc, quantidade_dias_no_mes,ano, mes_numerico, servidor)

        troca_de_dados = {
            "CAMPO SETOR": servidor['setor'],
            "CAMPO MÊS":  mes_por_extenso,
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

        caminho_pasta = f"setor/{troca_de_dados["CAMPO SETOR"]}/servidor/{mes_por_extenso}/{troca_de_dados["CAMPO NOME"]}"

        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)

        docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{str(troca_de_dados['CAMPO NOME'])}_FREQUÊNCIA_MENSAL.docx"))
        pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{str(troca_de_dados['CAMPO NOME'])}_FREQUÊNCIA_MENSAL.pdf"))

        doc.save(docx_path)
        convert_to_pdf(docx_path, pdf_path)

        return jsonify({'mensagem': 'Documento gerado com sucesso!'}), 200
        
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500

def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, servidor):
    linha_inicial = 8

    print(mes_numerico)
    for table in doc.tables:
            if len(table.rows) >= linha_inicial + quantidade_dias_no_mes:
                for i in range(quantidade_dias_no_mes):
                    dia_semana = pega_final_de_semana(ano, mes_numerico, i + 1)
                    dias = i + 1
                    row = table.rows[linha_inicial + i] 
                    dia_cell = row.cells[0] 

                    for paragraph in dia_cell.paragraphs: 
                        dia_cell.text = str(dias)

                    if dia_semana == 5:    
                        for paragraph in dia_cell.paragraphs:
                            row.cells[2].text = "SÁBADO"
                            row.cells[5].text = "SÁBADO"
                            row.cells[9].text = "SÁBADO"
                            row.cells[13].text = "SÁBADO"
                    elif dia_semana == 6:   
                        for paragraph in dia_cell.paragraphs:
                            row.cells[2].text = "DOMINGO"
                            row.cells[5].text = "DOMINGO"
                            row.cells[9].text = "DOMINGO"
                            row.cells[13].text = "DOMINGO"

                    
                    if servidor['feriasinicio'] is not None and servidor['feriasfinal'] is not None:
                        # Verifica se a data de referência está dentro do período de férias
                        if servidor['feriasinicio'] <= date(ano, mes_numerico, dias) <= servidor['feriasfinal']:
                            # Verifica se o dia da semana não é sábado (5) ou domingo (6)
                            if dia_semana not in [5, 6]:
                                
                                run = paragraph.add_run(str(dias))
                                row.cells[2].text = "FÉRIAS"
                                row.cells[5].text = "FÉRIAS"
                                row.cells[9].text = "FÉRIAS"
                                row.cells[13].text = "FÉRIAS"
            else:
                print(f"A tabela não tem linhas suficientes para os {quantidade_dias_no_mes} dias do mês.")