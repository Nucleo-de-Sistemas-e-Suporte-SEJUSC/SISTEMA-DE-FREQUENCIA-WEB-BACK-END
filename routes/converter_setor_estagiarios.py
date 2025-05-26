from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana # pega_quantidade_dias_mes removido pois não é usado aqui
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
# from mysql.connector import Error # Não usado diretamente
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ROW_HEIGHT_RULE
import os
import zipfile
from datetime import datetime, timedelta, date # Adicionado para cria_dias_da_celula

bp_converte_setor_estagiario_pdf = Blueprint('bp_converte_setor_estagiario_pdf', __name__)

@bp_converte_setor_estagiario_pdf.route('/api/setores/estagiar/pdf', methods=['POST']) # Rota alterada para clareza
def converte_setores_estagiarios_pdf(): # Função renomeada para clareza
    try:
        body = request.json or {}
        setores_nomes = body.get('setores')  # Nomes dos setores a serem filtrados (lista)
        mes_body = body.get('mes')

        if not setores_nomes or not isinstance(setores_nomes, list):
            return jsonify({'erro': 'Nenhum setor selecionado ou formato inválido'}), 400

        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']

        arquivos_zip_dos_setores = [] # Para armazenar caminhos dos zips específicos de cada setor

        for setor_nome in setores_nomes:
            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)

            # Busca todos os estagiários do setor especificado
            query = "SELECT * FROM estagiarios WHERE setor = %s"
            cursor.execute(query, (setor_nome,))
            estagiarios = cursor.fetchall()

            if not estagiarios:
                if conexao.is_connected():
                    conexao.close()
                print(f"Nenhum estagiário encontrado no setor {setor_nome}, pulando.")
                continue # Pula para o próximo setor

            arquivos_pdf_gerados_neste_setor = []
            setor_limpo = setor_nome.strip().replace('/', '_')
            caminho_pasta_base_setor = f"setor/estagiarios/{setor_limpo}/{mes_por_extenso}" # Adicionado 'estagiarios' ao caminho
            os.makedirs(caminho_pasta_base_setor, exist_ok=True)

            for estagiario in estagiarios:
                template_path = 'FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx'
                doc = Document(template_path)

                cria_dias_da_celula(doc, ano, mes_numerico, estagiario)

                troca_de_dados = {
                    "CAMPO SETOR": estagiario['setor'],
                    "CAMPO MÊS": mes_por_extenso,
                    "CAMPO NOME": estagiario['nome'],
                    "CAMPO ANO": str(ano),
                    "CAMPO HORARIO": str(estagiario.get('horario', '')), # Adicionado string vazia como padrão
                    "CAMPO ENTRADA": str(estagiario.get('horario_entrada', '')), # Adicionado string vazia como padrão
                    "CAMPO SAÍDA": str(estagiario.get('horario_saida', '')), # Adicionado string vazia como padrão
                    "CAMPO CARGO": str(estagiario.get('cargo', '')), # Adicionado string vazia como padrão
                }

                for placeholder, valor in troca_de_dados.items():
                    muda_texto_documento(doc, placeholder, valor)

                nome_limpo = estagiario['nome'].strip().replace('/', '_')

                nome_base = f"FREQUENCIA_ESTAGIARIO_{nome_limpo.replace(' ', '_')}" # Adicionado ESTAGIARIO ao nome do arquivo
                docx_path = os.path.abspath(os.path.join(caminho_pasta_base_setor, f"{nome_base}.docx"))
                pdf_path = os.path.abspath(os.path.join(caminho_pasta_base_setor, f"{nome_base}.pdf"))

                doc.save(docx_path)
                convert_to_pdf(docx_path, pdf_path)
                arquivos_pdf_gerados_neste_setor.append(pdf_path)

                # Salva no banco o caminho do PDF
                cursor.execute(
                    "INSERT INTO arquivos_pdf (servidor_id, caminho_pdf) VALUES (%s, %s)", # Adicionado tipo_servidor
                    (estagiario['id'], pdf_path)
                )

            if arquivos_pdf_gerados_neste_setor: # Só cria o zip se houver PDFs
                # Cria arquivo ZIP com todos os PDFs do setor de estagiários
                zip_path_setor = f"setor/estagiarios/{setor_limpo}/frequencias_estagiarios_{setor_limpo}_{mes_por_extenso}.zip" # Adicionado 'estagiarios'
                with zipfile.ZipFile(zip_path_setor, 'w') as zipf:
                    for pdf in arquivos_pdf_gerados_neste_setor:
                        zipf.write(pdf, os.path.basename(pdf))

                arquivos_zip_dos_setores.append(zip_path_setor)

                # Salva o ZIP do setor no banco
                cursor.execute(
                    "INSERT INTO arquivos_zip (setor, mes, caminho_zip, tipo) VALUES (%s, %s, %s, %s)",
                    (setor_nome, mes_por_extenso, zip_path_setor, 'estagiarios') # tipo 'estagiarios' para setor individual
                )

            conexao.commit()
            if conexao.is_connected():
                conexao.close()

        if not arquivos_zip_dos_setores:
            return jsonify({'erro': 'Nenhum arquivo ZIP de estagiários foi gerado para os setores selecionados'}), 404

        # Se mais de um setor de estagiários foi processado e gerou ZIPs, cria um ZIP final com todos os ZIPs dos setores
        if len(arquivos_zip_dos_setores) > 1:
            zip_final_path = f"setor/estagiarios/frequencias_multissetores_estagiarios_{mes_body}.zip" # Nome distinto
            with zipfile.ZipFile(zip_final_path, 'w') as zipf:
                for zip_file_setor in arquivos_zip_dos_setores:
                    zipf.write(zip_file_setor, os.path.basename(zip_file_setor))

            # Salva o ZIP de multissetores de estagiários no banco
            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO arquivos_zip (setor, mes, caminho_zip, tipo) VALUES (%s, %s, %s, %s)",
                ('multiestagiarios', mes_por_extenso, zip_final_path, 'multiestagiarios') # tipo 'multiestagiarios'
            )
            conexao.commit()
            if conexao.is_connected():
                conexao.close()

            return send_file(
                zip_final_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=os.path.basename(zip_final_path) # Usa basename para nome do download
            )
        elif arquivos_zip_dos_setores: # Apenas um setor foi processado ou gerou um ZIP
            return send_file(
                arquivos_zip_dos_setores[0],
                mimetype='application/zip',
                as_attachment=True,
                download_name=os.path.basename(arquivos_zip_dos_setores[0]) # Usa basename para nome do download
            )
        # Este caso 'else' idealmente seria capturado por "if not arquivos_zip_dos_setores" anteriormente

    except Exception as exception:
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()
        return jsonify({'erro': f'Erro ao processar setores de estagiários: {str(exception)}'}), 500

def cria_dias_da_celula(doc, ano, mes_numerico, estagiario):
    # from datetime import datetime, timedelta, date # Movido para imports de nível superior

    def calcula_periodo_21_a_20(ano_calc, mes_calc): # Parâmetros renomeados para evitar conflito
        data_inicio = datetime(ano_calc, mes_calc, 21)
        if mes_calc == 12:
            data_fim = datetime(ano_calc + 1, 1, 20)
        else:
            data_fim = datetime(ano_calc, mes_calc + 1, 20)

        dias_periodo = []
        data_atual_loop = data_inicio # Renomeado para evitar conflito
        while data_atual_loop <= data_fim:
            dias_periodo.append({
                "dia": data_atual_loop.day,
                "mes": data_atual_loop.month,
                "ano": data_atual_loop.year
            })
            data_atual_loop += timedelta(days=1)
        return dias_periodo

    linha_inicial = 7  # Ajuste conforme necessário

    for table in doc.tables:
        # Configurar linhas existentes
        for row_idx, row in enumerate(table.rows): # Use enumerate se o índice for necessário para linhas de cabeçalho específicas
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

        # Garante que a tabela tenha linhas suficientes antes de tentar acessá-las
        # Começa a adicionar linhas a partir do número atual de linhas até linha_inicial + len(dias_periodo)
        # Esta parte assume que o template tem *pelo menos* `linha_inicial` linhas.
        # Se o template puder ter menos, esta lógica precisa ser mais robusta.

        current_rows = len(table.rows)
        needed_data_rows = len(dias_periodo)
        total_needed_rows = linha_inicial + needed_data_rows

        if current_rows < total_needed_rows:
            for _ in range(total_needed_rows - current_rows):
                new_row = table.add_row()
                # Configure as propriedades das novas células da linha aqui se elas diferirem do padrão ou do loop acima
                new_row.height = Cm(0.55)
                new_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
                for cell_idx in range(len(table.columns)): # Assume que todas as linhas têm o mesmo número de colunas
                    new_cell = new_row.cells[cell_idx] # Acessa por índice se necessário
                    # new_cell.width = Cm(1.5) # Definir largura para células individuais pode ser complicado, geralmente feito no nível da coluna
                    for paragraph in new_cell.paragraphs:
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        # Adiciona um run padrão para definir propriedades da fonte se a célula estiver vazia
                        run = paragraph.add_run()
                        run.font.name = "Calibri"
                        run.font.size = Pt(7)


        # Preenchimento dos dias
        for i, dia_info in enumerate(dias_periodo):
            dia = dia_info["dia"]
            mes = dia_info["mes"]
            ano_dia = dia_info["ano"]

            if (linha_inicial + i) >= len(table.rows):
                print(f"AVISO: Tentando acessar linha {linha_inicial + i} que não existe. Dias: {len(dias_periodo)}, Linhas Tabela: {len(table.rows)}")
                # Isso não deve acontecer se a lógica de adição de linha acima estiver correta
                continue

            row = table.rows[linha_inicial + i]
            dia_semana = pega_final_de_semana(ano_dia, mes, dia)

            # Limpa células antes de preencher
            for cell_idx in range(len(row.cells)):
                cell = row.cells[cell_idx]
                # Limpa completamente o conteúdo existente
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.clear() # Limpa runs
                    if len(cell.paragraphs) > 1: # Se houver mais de um parágrafo, remove os extras
                        for p_extra_idx in range(len(cell.paragraphs) -1, 0, -1): # Itera de trás para frente para remover
                            p_extra = cell.paragraphs[p_extra_idx]
                            cell._element.remove(p_extra._p)
                # Garante que pelo menos um parágrafo exista e esteja limpo
                if not cell.paragraphs:
                    cell.add_paragraph()
                cell.paragraphs[0].clear() # Limpa o primeiro/principal parágrafo
                cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


            # Preenche dia
            dia_cell = row.cells[0]
            dia_paragraph = dia_cell.paragraphs[0] # Deve existir devido à lógica de limpeza
            # dia_paragraph.clear() # Já limpo acima
            dia_run = dia_paragraph.add_run(str(dia))
            dia_run.font.name = "Calibri"
            dia_run.font.size = Pt(8)
            dia_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            text_to_write = ""
            is_special_day = False

            # Verifica férias primeiro, as férias podem sobrepor o final de semana no texto
            if estagiario.get('feriasinicio') and estagiario.get('feriasfinal'):
                ferias_inicio = estagiario['feriasinicio']
                ferias_final = estagiario['feriasfinal']
                # Garante que ferias_inicio e ferias_final sejam objetos date se vierem do BD como datetime
                if hasattr(ferias_inicio, 'date'):
                    ferias_inicio = ferias_inicio.date()
                if hasattr(ferias_final, 'date'):
                    ferias_final = ferias_final.date()

                current_date_obj = date(ano_dia, mes, dia)

                if ferias_inicio <= current_date_obj <= ferias_final:
                    text_to_write = "FÉRIAS"
                    is_special_day = True

            # Se não for férias, verifica final de semana
            if not is_special_day:
                if dia_semana == 5:    # Sábado
                    text_to_write = "SÁBADO"
                    is_special_day = True
                elif dia_semana == 6:   # Domingo
                    text_to_write = "DOMINGO"
                    is_special_day = True

            if is_special_day:
                # Índices das células parecem ser [2, 5, 8, 12] conforme seu código original
                # Estes podem corresponder a colunas específicas como 'Entrada AM', 'Saida AM', 'Entrada PM', 'Saida PM'
                # Garanta que esses índices estejam corretos para o seu template.
                column_indices_for_special_text = [2, 5, 8, 12]
                for j in column_indices_for_special_text:
                    if j < len(row.cells):
                        cell = row.cells[j]
                        # cell.text = text_to_write # Usando add_run para melhor controle
                        p = cell.paragraphs[0] # Deve existir
                        # p.clear() # Já limpo
                        run = p.add_run(text_to_write)
                        run.font.bold = True
                        run.font.name = "Calibri" # Garante consistência da fonte
                        run.font.size = Pt(7)     # Garante consistência da fonte
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    else:
                        print(f"AVISO: Índice de coluna {j} fora do alcance para a linha {linha_inicial + i}")