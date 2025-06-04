#from utils.valida_ambiente_inux import valida_ambiente_pdf_linux
from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from mysql.connector import Error
from docx import Document
from docx.shared import Pt,Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ROW_HEIGHT_RULE
import os
import zipfile 
import datetime
from datetime import time, timedelta, datetime
from datetime import date
from dateutil.easter import easter
import holidays

bp_converte_estagiario_pdf = Blueprint('bp_converte_estagiario_pdf', __name__)

def pegar_feriados_mes(ano, mes, estado='AM', cidade=None):
    br_feriados = holidays.Brazil(state=estado)
    pascoa = easter(ano)
    corpus_christi = pascoa + timedelta(days=60)
    br_feriados[corpus_christi] = "Corpus Christi"

    feriados_municipais = {
        'Manaus': [
            date(ano, 10, 24),
        ]
    }
    if cidade in feriados_municipais:
        for feriado in feriados_municipais[cidade]:
            br_feriados[feriado] = "Feriado Municipal"

    # Pega feriados do mês e do mês seguinte (até dia 20)
    feriados_periodo = []
    for d in br_feriados:
        if (d.year == ano and d.month == mes) or \
           (d.year == ano and d.month == (mes % 12) + 1 and d.day <= 20) or \
           (mes == 12 and d.year == ano + 1 and d.month == 1 and d.day <= 20):
            feriados_periodo.append(d)
    return feriados_periodo


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
        feriados_do_mes = pegar_feriados_mes(ano, mes_numerico)

        for estagiario in estagiarios:
            template_path = 'FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx'
            doc = Document(template_path)

            cria_dias_da_celula(doc, ano, mes_numerico, estagiario, feriados_do_mes)

            troca_de_dados = {
                "CAMPO SETOR": estagiario['setor'],
                "CAMPO MES": mes_por_extenso,
                "CAMPO NOME": estagiario['nome'],
                #"CAMPO PERIODO": f"21/{mes_numerico}/{ano} a 20/{(mes_numerico % 12) + 1}/{ano if mes_numerico < 12 else ano + 1}",
                "CAMPO ANO": str(ano),
                "CAMPO HORARIO": str(estagiario.get('horario')),
                "CAMPO ENTRADA": formatar_horario_para_hh_mm_v2(estagiario.get('horario_entrada')),
                "CAMPO SAÍDA": formatar_horario_para_hh_mm_v2(estagiario.get('horario_saida')),
                "CAMPO CARGO": str(estagiario.get('cargo')),
            }

            for placeholder, valor in troca_de_dados.items():
                muda_texto_documento(doc, placeholder, valor)
            nome_limpo = estagiario['nome'].strip()
            setor_limpo = estagiario['setor'].replace('/', '-').strip()
            caminho_pasta = f"setor/{setor_limpo}/estagiario/{mes_por_extenso}/{nome_limpo}"
            os.makedirs(caminho_pasta, exist_ok=True)

            nome_base = f"{nome_limpo.replace(' ', '_')}_FREQUENCIA"
            docx_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.docx"))
            pdf_path = os.path.abspath(os.path.join(caminho_pasta, f"{nome_base}.pdf"))

            
            doc.save(docx_path)
            convert_to_pdf(docx_path, pdf_path)

            arquivos_gerados.append(pdf_path)
            


        # Cria um arquivo ZIP com todos os PDFs
        zip_path = f"setor/frequencias_{mes_por_extenso}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for pdf in arquivos_gerados:
                zipf.write(pdf, os.path.basename(pdf))

        # Salva o ZIP no banco
        cursor.execute(
            "INSERT INTO arquivos_zip (mes, caminho_zip, tipo) VALUES (%s, %s,%s)",
            (mes_por_extenso, zip_path, 'estagiario')
        )

        conexao.commit()
        conexao.close()

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
    
    
def cria_dias_da_celula(doc, ano, mes_numerico, estagiario, feriados):
    from datetime import datetime, timedelta, date # 'date' é importante aqui

    def calcula_periodo_21_a_20(ano_calc, mes_calc): # Renomeei os parâmetros para evitar conflito
        data_inicio = datetime(ano_calc, mes_calc, 21)
        if mes_calc == 12:
            data_fim = datetime(ano_calc + 1, 1, 20)
        else:
            data_fim = datetime(ano_calc, mes_calc + 1, 20)

        dias_periodo = []
        # Renomeei 'data_atual' aqui para 'data_iter_calc' para clareza
        data_iter_calc = data_inicio
        while data_iter_calc <= data_fim:
            dias_periodo.append({
                "dia": data_iter_calc.day,
                "mes": data_iter_calc.month,
                "ano": data_iter_calc.year
            })
            data_iter_calc += timedelta(days=1)
        # O print que você tinha já mostra que esta parte funciona
        # print(f"Dias do período de 21 a 20: {dias_periodo}")
        return dias_periodo

    linha_inicial = 7

    for table in doc.tables:
        # ... (Configuração das linhas existentes) ...
        for row_idx, row in enumerate(table.rows): # Adicionado enumerate para debug, se necessário
            row.height = Cm(0.55)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    for run in paragraph.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(7)
                        run.font.bold = False


        dias_periodo = calcula_periodo_21_a_20(ano, mes_numerico)
        linhas_necessarias = linha_inicial + len(dias_periodo)

        if len(table.rows) < linhas_necessarias:
            for _ in range(linhas_necessarias - len(table.rows)):
                new_row = table.add_row()
                # É importante configurar as células da nova linha também, se necessário
                # Ex: new_row.height = Cm(0.55); new_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
                # for cell in new_row.cells: cell.width = Cm(1.5) ... etc.


        for i, dia_info in enumerate(dias_periodo):
            dia = dia_info["dia"]
            mes_iter = dia_info["mes"]
            ano_dia = dia_info["ano"]

            # Verifica se é o último dia do período (dia 20)
            is_ultimo_dia = (i == len(dias_periodo) - 1) or (dia == 20 and (i == len(dias_periodo) - 1))

            # ***** CORREÇÃO PRINCIPAL *****
            # Defina a data da iteração atual AQUI
            data_iteracao_atual = date(ano_dia, mes_iter, dia)
            # ******************************

            dia_semana = pega_final_de_semana(ano_dia, mes_iter, dia) # Use mes_iter
            
            # Verifica se a linha existe antes de acessá-la
            if (linha_inicial + i) >= len(table.rows):
                print(f"Aviso: Tentando acessar linha {linha_inicial + i}, mas a tabela tem apenas {len(table.rows)} linhas. Adicionando nova linha.")
                # Poderia adicionar uma nova linha aqui se a lógica anterior de adicionar linhas falhar ou não cobrir todos os casos
                # table.add_row() # Isso pode dessincronizar a formatação se não for manuseado com cuidado
                # Contudo, a lógica de adicionar linhas extras acima deveria prevenir isso.
                # Se este erro ocorrer, revise a lógica de adição de linhas.
                continue # Pula esta iteração para evitar erro de índice

            row = table.rows[linha_inicial + i]
            
            print(f"Row {linha_inicial + i} tem {len(row.cells)} células")
               
            for cell in row.cells:
                cell.text = ""
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    paragraph.clear()
            
            dia_cell = row.cells[0]
            dia_paragraph = dia_cell.paragraphs[0]
            dia_run = dia_paragraph.add_run(str(dia))
            dia_run.font.name = "Calibri"
            dia_run.font.size = Pt(8)
            dia_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            # Agora use 'data_iteracao_atual'
            is_feriado = data_iteracao_atual in feriados
            is_ferias = False

            if estagiario.get('feriasinicio') and estagiario.get('feriasfinal'):
                # Certifique-se que 'feriasinicio' e 'feriasfinal' são objetos date
                # Se forem datetime, converta com .date()
                ferias_inicio = estagiario['feriasinicio']
                if isinstance(ferias_inicio, datetime):
                    ferias_inicio = ferias_inicio.date()
                
                ferias_final = estagiario['feriasfinal']
                if isinstance(ferias_final, datetime):
                    ferias_final = ferias_final.date()

                if ferias_inicio <= data_iteracao_atual <= ferias_final:
                    is_ferias = True

            if dia_semana == 5:    # Sábado
                texto = "SÁBADO"
            elif dia_semana == 6:   # Domingo
                texto = "DOMINGO"
            elif is_ferias and dia_semana not in [5, 6]: # Férias (e não é fim de semana)
                texto = "FÉRIAS"
            elif is_feriado and dia_semana not in [5, 6]: # Feriado (e não é fim de semana nem férias já marcadas)
                texto = "FERIADO"
            else:
                texto = None # Dia normal de trabalho

            if texto:
                # Células para SÁBADO, DOMINGO, FÉRIAS: [2, 5, 8, 12]
                # Células para FERIADO: [2, 5, 9, 13] - ATENÇÃO: Diferente! Verifique se está correto.
                celulas_para_marcar = [2, 5, 8, 12]
                if texto == "FERIADO":
                     celulas_para_marcar = [2, 5, 9] # Manteve a lógica original, mas verifique.

                for j in celulas_para_marcar:
                    if j < len(row.cells): # Verificação de segurança
                        cell = row.cells[j]
                        # Limpar parágrafos existentes para evitar texto duplicado
                        for p in cell.paragraphs:
                            p.clear()
                        # Adicionar novo parágrafo com o texto
                        p_cell = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
                        run_cell = p_cell.add_run(texto)
                        run_cell.font.bold = True
                        run_cell.font.name = "Calibri" # Garante a formatação
                        run_cell.font.size = Pt(7)     # Garante a formatação
                        p_cell.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    else:
                        print(f"Aviso: Índice de célula {j} fora do alcance para a linha.")
            if len(row.cells) != 13:
                print(f"Linha {linha_inicial + i} ignorada por ter {len(row.cells)} células.")
                continue
            if is_ultimo_dia:
                # Aqui você pode aplicar qualquer lógica especial para a linha do dia 20
                print(f"Tratando linha especial para o dia 20: {dia}/{mes_iter}/{ano_dia}")
                # Exemplo: garantir que a linha tenha 13 células
                if len(row.cells) != 13:
                    print(f"Ajustando número de células da linha do dia 20")
                    # Adicione células ou trate conforme necessário
                # Ou aplicar formatação diferente, texto, etc.