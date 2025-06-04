from utils.convert_to_pdf import convert_to_pdf
from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ROW_HEIGHT_RULE
import os
import zipfile
from datetime import datetime, timedelta, date, time
# Imports necessários para pegar_feriados_mes
from dateutil.easter import easter
import holidays

bp_converte_setor_estagiario_pdf = Blueprint('bp_converte_setor_estagiario_pdf', __name__)

# COPIADO DE: Função pegar_feriados_mes (com seus prints de debug)
def pegar_feriados_mes(ano, mes, estado='AM'):
    print(f"DEBUG setor_estagiarios: Iniciando pegar_feriados_mes para ano={ano}, mes={mes}, estado='{estado}'")

    br_feriados = holidays.Brazil(state=estado)
    pascoa = easter(ano)
    corpus_christi = pascoa + timedelta(days=60)
    br_feriados[corpus_christi] = "Corpus Christi"

    conexao_feriado = None
    try:
        conexao_feriado = connect_mysql()
        cursor_feriado = conexao_feriado.cursor(dictionary=True)
        feriados_municipais_db = []
        query_sql = "SELECT data FROM feriados_municipais WHERE estado = %s AND YEAR(data) = %s"
        params = (estado, ano)
        print(f"DEBUG setor_estagiarios: Executando SQL: {query_sql} com params {params}")
        cursor_feriado.execute(query_sql, params)
        feriados_municipais_db = cursor_feriado.fetchall()
        print(f"DEBUG setor_estagiarios: Feriados municipais crus do DB: {feriados_municipais_db}")
        if feriados_municipais_db and feriados_municipais_db[0].get('data') is not None:
            print(f"DEBUG setor_estagiarios: Tipo do valor 'data' do primeiro feriado do DB (se existir): {type(feriados_municipais_db[0]['data'])}")
        cursor_feriado.close() # Fechar cursor aqui
    except Exception as e:
        print(f"DEBUG setor_estagiarios: Erro ao buscar feriados municipais do DB: {e}")
    finally:
        if conexao_feriado and conexao_feriado.is_connected():
            conexao_feriado.close()
            print("DEBUG setor_estagiarios: Conexão de feriado com MySQL fechada.")
        else:
            print("DEBUG setor_estagiarios: Conexão de feriado com MySQL já estava fechada ou não foi estabelecida.")

    for feriado_row in feriados_municipais_db:
        data_db = feriado_row['data']
        data_feriado_obj = None
        if data_db is None:
            continue
        if hasattr(data_db, 'date'):
            data_feriado_obj = data_db.date()
        elif isinstance(data_db, date):
            data_feriado_obj = data_db
        else:
            try:
                data_feriado_obj = date.fromisoformat(str(data_db))
            except ValueError:
                print(f"DEBUG setor_estagiarios: Alerta: Formato de data inválido '{data_db}' não pôde ser convertido.")
                continue
        if data_feriado_obj:
            br_feriados[data_feriado_obj] = "Feriado Municipal"
    # print(f"DEBUG setor_estagiarios: Conteúdo de br_feriados ANTES de filtrar por mês: {br_feriados.items()}")
    feriados_mes = [d for d in br_feriados if d.month == mes]
    print(f"DEBUG setor_estagiarios: Feriados filtrados para o mês {mes}: {feriados_mes}")
    return feriados_mes
# FIM DE: Função pegar_feriados_mes


def formatar_horario_para_hh_mm_v2(valor_horario):
    if not valor_horario: return ''
    if isinstance(valor_horario, time): return valor_horario.strftime('%H:%M')
    if isinstance(valor_horario, timedelta):
        total_seconds = abs(int(valor_horario.total_seconds()))
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    if isinstance(valor_horario, str):
        try:
            if valor_horario.count(':') == 2: return datetime.strptime(valor_horario, '%H:%M:%S').strftime('%H:%M')
            elif valor_horario.count(':') == 1: return datetime.strptime(valor_horario, '%H:%M').strftime('%H:%M')
            return valor_horario
        except ValueError: return valor_horario
    return str(valor_horario)


@bp_converte_setor_estagiario_pdf.route('/api/setores/estagiar/pdf', methods=['POST'])
def converte_setores_estagiarios_pdf():
    conexao_principal = None # Para ser usado no try/finally da rota
    try:
        body = request.json or {}
        setores_nomes = body.get('setores')
        mes_body = body.get('mes')

        if not setores_nomes or not isinstance(setores_nomes, list):
            return jsonify({'erro': 'Nenhum setor selecionado ou formato inválido'}), 400

        data_ano_mes_atual = data_atual(mes_body)
        mes_por_extenso = data_ano_mes_atual['mes']
        mes_numerico = data_ano_mes_atual['mes_numerico']
        ano = data_ano_mes_atual['ano']

        # --- Busca de feriados para o período intermensal (ANTES do loop de setores) ---
        estado_para_feriados = 'AM' # Defina o estado padrão ou obtenha dinamicamente se necessário globalmente

        feriados_mes_corrente_periodo = pegar_feriados_mes(ano, mes_numerico, estado=estado_para_feriados)
        
        ano_proximo_mes_periodo = ano
        mes_numerico_proximo_periodo = mes_numerico + 1
        if mes_numerico_proximo_periodo > 12:
            mes_numerico_proximo_periodo = 1
            ano_proximo_mes_periodo += 1
        feriados_proximo_mes_periodo = pegar_feriados_mes(ano_proximo_mes_periodo, mes_numerico_proximo_periodo, estado=estado_para_feriados)
        
        todos_feriados_do_periodo = list(set(feriados_mes_corrente_periodo + feriados_proximo_mes_periodo))
        print(f"DEBUG ROTA setor_estagiarios: Todos feriados para o período (mes {mes_numerico} e {mes_numerico_proximo_periodo}): {todos_feriados_do_periodo}")
        # --- FIM da busca de feriados ---

        arquivos_zip_dos_setores = []

        for setor_nome in setores_nomes:
            conexao_principal = connect_mysql() # Conexão por setor
            cursor = conexao_principal.cursor(dictionary=True)

            query = "SELECT * FROM estagiarios WHERE setor = %s"
            cursor.execute(query, (setor_nome,))
            estagiarios = cursor.fetchall()

            if not estagiarios:
                if conexao_principal and conexao_principal.is_connected():
                    cursor.close()
                    conexao_principal.close()
                print(f"Nenhum estagiário encontrado no setor {setor_nome}, pulando.")
                continue

            arquivos_pdf_gerados_neste_setor = []
            setor_limpo = setor_nome.strip().replace('/', '_')
            caminho_pasta_base_setor = f"setor/estagiarios/{setor_limpo}/{mes_por_extenso}"
            os.makedirs(caminho_pasta_base_setor, exist_ok=True)

            for estagiario in estagiarios:
                template_path = 'FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx'
                doc = Document(template_path)
                
                # Passa a lista de feriados combinada
                cria_dias_da_celula(doc, ano, mes_numerico, estagiario, todos_feriados_do_periodo)

                troca_de_dados = {
                    "CAMPO SETOR": estagiario.get('setor', ''),
                    "CAMPO MÊS": mes_por_extenso,
                    "CAMPO NOME": estagiario.get('nome', ''),
                    "CAMPO ANO": str(ano),
                    "CAMPO HORARIO": str(estagiario.get('horario', '')),
                    "CAMPO ENTRADA": formatar_horario_para_hh_mm_v2(estagiario.get('horario_entrada', '')),
                    "CAMPO SAÍDA": formatar_horario_para_hh_mm_v2(estagiario.get('horario_saida', '')),
                    "CAMPO CARGO": str(estagiario.get('cargo', '')),
                }
                for placeholder, valor in troca_de_dados.items():
                    muda_texto_documento(doc, placeholder, valor)

                nome_limpo = estagiario.get('nome', 'NOME_PADRAO').strip().replace('/', '_')
                nome_base = f"FREQUENCIA_ESTAGIARIO_{nome_limpo.replace(' ', '_')}"
                docx_path = os.path.abspath(os.path.join(caminho_pasta_base_setor, f"{nome_base}.docx"))
                pdf_path = os.path.abspath(os.path.join(caminho_pasta_base_setor, f"{nome_base}.pdf"))
                doc.save(docx_path)
                convert_to_pdf(docx_path, pdf_path)
                arquivos_pdf_gerados_neste_setor.append(pdf_path)
                cursor.execute(
                    "INSERT INTO arquivos_pdf (servidor_id, caminho_pdf) VALUES (%s, %s)",
                    (estagiario['id'], pdf_path)
                )

            if arquivos_pdf_gerados_neste_setor:
                zip_path_setor = f"setor/estagiarios/{setor_limpo}/frequencias_estagiarios_{setor_limpo}_{mes_por_extenso}.zip"
                with zipfile.ZipFile(zip_path_setor, 'w') as zipf:
                    for pdf in arquivos_pdf_gerados_neste_setor:
                        zipf.write(pdf, os.path.basename(pdf))
                arquivos_zip_dos_setores.append(zip_path_setor)
                cursor.execute(
                    "INSERT INTO arquivos_zip (setor, mes, caminho_zip, tipo) VALUES (%s, %s, %s, %s)",
                    (setor_nome, mes_por_extenso, zip_path_setor, 'estagiarios_setor') # tipo ajustado
                )
            conexao_principal.commit()
            if conexao_principal and conexao_principal.is_connected():
                cursor.close()
                conexao_principal.close()
        
        if not arquivos_zip_dos_setores:
            return jsonify({'message': 'Nenhum arquivo ZIP de estagiários foi gerado (sem estagiários nos setores ou sem PDFs).'}), 200 # Mudado para 200 com mensagem

        if len(arquivos_zip_dos_setores) > 1:
            zip_final_path = f"setor/estagiarios/frequencias_multissetores_estagiarios_{mes_body.replace('/','-')}_{ano}.zip" # Nome com ano e mes sem barra
            with zipfile.ZipFile(zip_final_path, 'w') as zipf:
                for zip_file_setor in arquivos_zip_dos_setores:
                    zipf.write(zip_file_setor, os.path.basename(zip_file_setor))
            
            # Salva o ZIP de multissetores (opcional, pode já ter sido salvo por setor)
            # Se for salvar, precisa de uma conexão
            conexao_principal = connect_mysql()
            cursor = conexao_principal.cursor(dictionary=True)
            cursor.execute(
                "INSERT INTO arquivos_zip (setor, mes, ano, caminho_zip, tipo) VALUES (%s, %s, %s, %s, %s)", # Adicionado ano
                ('multiestagiarios', mes_por_extenso, str(ano), zip_final_path, 'multiestagiarios_geral') # tipo ajustado
            )
            conexao_principal.commit()
            if conexao_principal and conexao_principal.is_connected():
                cursor.close()
                conexao_principal.close()

            return send_file(zip_final_path, mimetype='application/zip', as_attachment=True, download_name=os.path.basename(zip_final_path))
        elif arquivos_zip_dos_setores:
            return send_file(arquivos_zip_dos_setores[0], mimetype='application/zip', as_attachment=True, download_name=os.path.basename(arquivos_zip_dos_setores[0]))
        
        return jsonify({'message': 'Processamento concluído, mas nenhum ZIP para enviar (caso de um único setor sem PDFs).'}), 200

    except Exception as exception:
        print(f"ERRO ROTA SETOR ESTAGIARIOS: {str(exception)}")
        # import traceback; traceback.print_exc(); # Para debug detalhado
        if conexao_principal and conexao_principal.is_connected():
            cursor.close() # Garante que o cursor seja fechado se foi aberto
            conexao_principal.close()
        return jsonify({'erro': f'Erro ao processar setores de estagiários: {str(exception)}'}), 500

# Modificado para aceitar 'feriados' e aplicar a lógica
def cria_dias_da_celula(doc, ano_param, mes_param, estagiario, feriados): # Adicionado 'feriados'
    def calcula_periodo_21_a_20(ano_calc, mes_calc):
        data_inicio = datetime(ano_calc, mes_calc, 21)
        if mes_calc == 12: data_fim = datetime(ano_calc + 1, 1, 20)
        else: data_fim = datetime(ano_calc, mes_calc + 1, 20)
        dias_periodo = []
        data_atual_loop = data_inicio
        while data_atual_loop <= data_fim:
            dias_periodo.append({"dia": data_atual_loop.day, "mes": data_atual_loop.month, "ano": data_atual_loop.year})
            data_atual_loop += timedelta(days=1)
        return dias_periodo

    linha_inicial = 7
    for table in doc.tables:
        for row in table.rows: # Configurações básicas de formatação
            row.height = Cm(0.55); row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    for run in paragraph.runs: run.font.name = "Calibri"; run.font.size = Pt(7); run.font.bold = False
        
        dias_periodo = calcula_periodo_21_a_20(ano_param, mes_param)
        total_needed_rows = linha_inicial + len(dias_periodo)
        while len(table.rows) < total_needed_rows:
            new_row = table.add_row()
            new_row.height = Cm(0.55); new_row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for cell_idx in range(len(table.columns)):
                new_cell = new_row.cells[cell_idx]
                p = new_cell.paragraphs[0] if new_cell.paragraphs else new_cell.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                if not p.runs: run = p.add_run(); run.font.name = "Calibri"; run.font.size = Pt(7)

        for i, dia_info in enumerate(dias_periodo):
            dia, mes_iter, ano_dia = dia_info["dia"], dia_info["mes"], dia_info["ano"]
            row = table.rows[linha_inicial + i]
            
            for cell in row.cells: # Limpeza de células
                for p in cell.paragraphs: p.clear()
                p_cell = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph(); p_cell.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

            dia_run = row.cells[0].paragraphs[0].add_run(str(dia)) # Dia
            dia_run.font.name = "Calibri"; dia_run.font.size = Pt(8)

            current_date_obj = date(ano_dia, mes_iter, dia)
            dia_semana = pega_final_de_semana(ano_dia, mes_iter, dia)
            text_to_write = None

            if estagiario.get('feriasinicio') and estagiario.get('feriasfinal'):
                ferias_inicio_raw = estagiario['feriasinicio']
                ferias_final_raw = estagiario['feriasfinal']
                ferias_inicio = ferias_inicio_raw.date() if isinstance(ferias_inicio_raw, datetime) else ferias_inicio_raw
                ferias_final = ferias_final_raw.date() if isinstance(ferias_final_raw, datetime) else ferias_final_raw
                if isinstance(ferias_inicio, date) and isinstance(ferias_final, date) and (ferias_inicio <= current_date_obj <= ferias_final):
                    text_to_write = "FÉRIAS"
            
            if text_to_write is None and current_date_obj in feriados and dia_semana not in [5, 6]:
                text_to_write = "FERIADO"
            
            if text_to_write is None:
                if dia_semana == 5: text_to_write = "SÁBADO"
                elif dia_semana == 6: text_to_write = "DOMINGO"
            
            if text_to_write:
                column_indices = [2, 5, 8, 12] # Padrão para SÁBADO, DOMINGO, FÉRIAS
                if text_to_write == "FERIADO": # Seu código original especificava colunas diferentes para FERIADO de estagiário
                     column_indices = [2, 5, 9] # Verifique se isto está correto para o template de estagiário
                
                for j_idx in column_indices:
                    if j_idx < len(row.cells):
                        cell_marcar = row.cells[j_idx]
                        p_marcar = cell_marcar.paragraphs[0]
                        run_marcar = p_marcar.add_run(text_to_write)
                        run_marcar.font.bold = True; run_marcar.font.name = "Calibri"; run_marcar.font.size = Pt(7)