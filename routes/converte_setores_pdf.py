from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from datetime import datetime, date
import os

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
        if mes_body is not None:
            data_ano_mes_atual = data_atual(mes_body)
            mes_por_extenso = data_ano_mes_atual['mes']
            mes_numerico = data_ano_mes_atual['mes_numerico']
        else: 
            data_ano_mes_atual = data_atual(mes_informado_pelo_usuario=None)
            mes_por_extenso = data_ano_mes_atual['mes'] 
            mes_numerico = data_ano_mes_atual['mes_numerico']
            
        ano = data_ano_mes_atual['ano']
        quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)

        template_path = 'FREQUÊNCIA_MENSAL.docx'

        # Consulta funcionários do setor informado
        busca_setor = "SELECT * FROM funcionarios WHERE setor = %s"
        cursor.execute(busca_setor, (setor,))
        setores = cursor.fetchall()

        if len(setores) == 0:
            conexao.close()
            return jsonify({'erro': 'Setor não encontrado'}), 404

        for setor in setores:
            caminho_pasta = f"setor/{setor['setor']}/servidor/{mes_por_extenso}/{setor['nome']}"
            os.makedirs(caminho_pasta, exist_ok=True)

            docx_path = os.path.join(caminho_pasta, f"{setor['nome']}_FREQUÊNCIA_MENSAL.docx")
            pdf_path = os.path.join(caminho_pasta, f"{setor['nome']}_FREQUÊNCIA_MENSAL.pdf")

            # Criação do documento Word baseado no template
            doc = Document(template_path)

            # Substitui os placeholders pelos valores reais ou uma string padrão se forem None
            placeholders = {
                "CAMPO SETOR": str(setor.get('setor', "SEM DADOS")),
                "CAMPO MÊS": mes_por_extenso,
                "CAMPO ANO": str(ano),
                "CAMPO NOME": str(setor.get('nome', "SEM DADOS")),
                "CAMPO MATRÍCULA": str(setor.get('matricula', "SEM DADOS")),
                "CAMPO CARGO": str(setor.get('cargo', "SEM DADOS")),
                "CAMPO FUNÇÃO": str(setor.get('funcao', "SEM DADOS")),
                "CAMPO HORARIO": str(setor.get('horario', "SEM DADOS")),
                "CAMPO ENTRADA": str(setor.get('horarioentrada', "SEM DADOS")),
                "CAMPO SAÍDA": str(setor.get('horariosaida', "SEM DADOS")),
                "FERIAS INICIO": str(setor.get('feriasinicio', "")),
                "FERIAS TERMINO": str(setor.get('feriasfinal', "")),
            }

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for placeholder, valor in placeholders.items():
                                if placeholder in paragraph.text:
                                    paragraph.text = paragraph.text.replace(placeholder, valor)

            # Preenche os dias no calendário
            linha_inicial = 8  # Linha onde começam os dias no template
            for table in doc.tables:
                if len(table.rows) >= linha_inicial + quantidade_dias_no_mes:
                    for i in range(quantidade_dias_no_mes):
                        dia_semana = pega_final_de_semana(ano, mes_numerico, i + 1)
                        dia_cell = table.rows[linha_inicial + i].cells[0]
                        dia_cell.text = str(i + 1)  # Preenche o número do dia

                        # Preenche sábados e domingos com texto específico
                        if dia_semana == 5:  # Sábado
                            for j in [2, 5, 9, 13]:
                                table.rows[linha_inicial + i].cells[j].text = "SÁBADO"
                        elif dia_semana == 6:  # Domingo
                            for j in [2, 5, 9, 13]:
                                table.rows[linha_inicial + i].cells[j].text = "DOMINGO"

                        # Preenche férias se aplicável
                        ferias_inicio = setor.get('feriasinicio')
                        ferias_final = setor.get('feriasfinal')
                        dia_atual = date(ano, mes_numerico, i + 1)
                        if ferias_inicio and ferias_final and ferias_inicio <= dia_atual <= ferias_final and dia_semana not in [5, 6]:
                            for j in [2, 5, 9, 13]:
                                table.rows[linha_inicial + i].cells[j].text = "FÉRIAS"

            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

        return jsonify({'mensagem': 'Documentos gerados com sucesso!'}), 200
        
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500
