from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from docx import Document
from datetime import datetime, date
import os
import calendar
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 
# Importa o decorador personalizado


bp_converte_setor_pdf = Blueprint('bp_converte_setor_pdf', __name__)

@bp_converte_setor_pdf.route('/api/setores/pdf/<setor>', methods=['GET'])
@login_required
@roles_required('admin','editor')
def converte_setores_pf(setor):
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

        busca_setor = "SELECT * FROM funcionarios WHERE setor = %s"
        cursor.execute(busca_setor, (setor,))
        setores = cursor.fetchall()

        if (len(setores) == 0):
            conexao.close()
            return jsonify({'erro': 'Setor não encontrado'}), 404

        dados_setores = []

        linha_inicial = 8       

        for setor in setores:

            troca_dados_setor = {
                "CAMPO SETOR": setor['setor'],
                "CAMPO MÊS": data_ano_mes_atual['mes'],
                "CAMPO NOME": setor['nome'],
                "CAMPO ANO": str(data_ano_mes_atual['ano']),
                "CAMPO HORARIO": str(setor['horario']),
                "CAMPO ENTRADA": str(setor['horarioentrada']),
                "CAMPO SAÍDA": str(setor['horariosaida']),
                "CAMPO MATRÍCULA": str(setor['matricula']),
                "CAMPO CARGO": setor['cargo'],
                "CAMPO FUNÇÃO": str(setor['funcao']),
                "FERIAS INICIO": setor['feriasinicio'],
                "FERIAS TERMINO": setor['feriasfinal'],
            }

            dados_setores.append(troca_dados_setor)
        

        def cria_dias_da_celula(doc, quantidade_dias_no_mes, ano, mes_numerico, setor):
            linha_inicial = 8

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

                            if setor['FERIAS INICIO'] is not None and setor['FERIAS TERMINO'] is not None:
                                # Verifica se a data de referência está dentro do período de férias
                                if setor['FERIAS INICIO'] <= date(ano, mes_numerico, dias) <= setor['FERIAS TERMINO']:
                                    # Verifica se o dia da semana não é sábado (5) ou domingo (6)
                                    if dia_semana not in [5, 6]:
                                        run = paragraph.add_run(str(dias))
                                        row.cells[2].text = "FÉRIAS"
                                        row.cells[5].text = "FÉRIAS"
                                        row.cells[9].text = "FÉRIAS"
                                        row.cells[13].text = "FÉRIAS"
                    else:
                        print(f"A tabela não tem linhas suficientes para os {quantidade_dias_no_mes} dias do mês.")
                


        for dado_setor in dados_setores:    
            doc = Document(template_path)

            gera_dados_celula = cria_dias_da_celula(doc, quantidade_dias_no_mes,ano, mes_numerico, dado_setor)


            for placeholder, valor in dado_setor.items():
                muda_texto_documento(doc, placeholder, valor)

            caminho_pasta = f"setor/{dado_setor['CAMPO SETOR']}/servidor/{data_ano_mes_atual['mes']}/{dado_setor['CAMPO NOME']}"

            if not os.path.exists(caminho_pasta):
                os.makedirs(caminho_pasta)

            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{str(dado_setor['CAMPO NOME'])}_FREQUÊNCIA_MENSAL.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{str(dado_setor['CAMPO NOME'])}_FREQUÊNCIA_MENSAL.pdf"))

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)    

        return jsonify({'mensagem': 'Documentos gerados com sucesso!'}), 200
        
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500



