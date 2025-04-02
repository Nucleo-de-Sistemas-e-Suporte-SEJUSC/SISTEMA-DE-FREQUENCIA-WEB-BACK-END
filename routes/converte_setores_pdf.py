from utils.muda_texto_documento import muda_texto_documento
from utils.formata_datas import data_atual, pega_final_de_semana, pega_quantidade_dias_mes
from flask import Blueprint, request, jsonify, send_file
from conection_mysql import connect_mysql
from docx import Document
from datetime import datetime, date
from utils.convert_to_pdf import convert_to_pdf
import os
import re
import shutil
import logging
from contextlib import closing
from unidecode import unidecode

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp_converte_setor_pdf = Blueprint('bp_converte_setor_pdf', __name__)
TEMPLATE_PATH = 'FREQUÊNCIA_MENSAL.docx'
CELULAS_DIAS = [2, 5, 9, 13]
LINHA_INICIAL_DIAS = 8

def validar_mes(mes_body):
    """Valida o formato do mês YYYY-MM"""
    if mes_body and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', mes_body):
        raise ValueError("Formato de mês inválido. Use YYYY-MM (ex: 2025-04)")

def criar_pasta_temp(mes_por_extenso):
    """Cria pasta temporária com timestamp único"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    pasta_temp = f"temp/{mes_por_extenso}_{timestamp}"
    os.makedirs(pasta_temp, exist_ok=True)
    return pasta_temp

def processar_servidor(servidor, mes_por_extenso, mes_numerico, ano, quantidade_dias_no_mes, pasta_temp):
    """Processa um único servidor e gera seus documentos"""
    try:
        # Verifica template
        if not os.path.exists(TEMPLATE_PATH):
            raise FileNotFoundError(f"Arquivo template não encontrado: {TEMPLATE_PATH}")

        doc = Document(TEMPLATE_PATH)

        # Preenche os dias do mês
        for table in doc.tables:
            if len(table.rows) >= LINHA_INICIAL_DIAS + quantidade_dias_no_mes:
                for i in range(quantidade_dias_no_mes):
                    dia = i + 1
                    dia_semana = pega_final_de_semana(ano, mes_numerico, dia)
                    row = table.rows[LINHA_INICIAL_DIAS + i]
                    row.cells[0].text = str(dia)

                    # Marca fins de semana
                    if dia_semana == 5:  # Sábado
                        texto = "SÁBADO"
                    elif dia_semana == 6:  # Domingo
                        texto = "DOMINGO"
                    else:
                        texto = None

                    if texto:
                        for cell_index in CELULAS_DIAS:
                            row.cells[cell_index].text = texto

                    # Verifica férias
                    if servidor.get('feriasinicio') and servidor.get('feriasfinal'):
                        data_dia = date(ano, mes_numerico, dia)
                        ferias_inicio = servidor['feriasinicio']
                        ferias_final = servidor['feriasfinal']
                        
                        if ferias_inicio <= data_dia <= ferias_final and dia_semana not in [5, 6]:
                            for cell_index in CELULAS_DIAS:
                                row.cells[cell_index].text = "FÉRIAS"

        # Substituição de placeholders
        campos = {
            "CAMPO SETOR": servidor.get('setor', ''),
            "CAMPO MÊS": mes_por_extenso,
            "CAMPO NOME": servidor.get('nome', ''),
            "CAMPO ANO": str(ano),
            "CAMPO HORARIO": servidor.get('horario', ''),
            "CAMPO ENTRADA": servidor.get('horarioentrada', ''),
            "CAMPO SAÍDA": servidor.get('horariosaida', ''),
            "CAMPO MATRÍCULA": servidor.get('matricula', ''),
            "CAMPO CARGO": servidor.get('cargo', ''),
            "CAMPO FUNÇÃO": servidor.get('funcao', ''),
        }

        for placeholder, valor in campos.items():
            if valor is not None:
                muda_texto_documento(doc, placeholder, str(valor))

        # Geração de arquivos
        nome_limpo = unidecode(servidor['nome'])  # Remove acentos
        nome_limpo = ''.join(c for c in nome_limpo if c.isalnum() or c in ' _-')  # Remove caracteres especiais
        nome_base = f"{servidor['matricula']}_FREQ_{mes_numerico}_{ano}"[:50]

        docx_path = os.path.join(pasta_temp, f"{nome_base}.docx")
        pdf_path = os.path.join(pasta_temp, f"{nome_base}.pdf")

        # Salva DOCX
        doc.save(docx_path)
        logger.info(f"Documento DOCX gerado: {docx_path}")

        # Converte para PDF
        if not convert_to_pdf(docx_path, pdf_path):
            raise RuntimeError("Falha na conversão para PDF")
        
        if not os.path.exists(pdf_path):
            raise RuntimeError("Arquivo PDF não foi gerado")

        logger.info(f"Documento PDF gerado: {pdf_path}")

        return {
            'nome': servidor['nome'],
            'matricula': servidor['matricula'],
            'setor': servidor['setor'],
            'documento': f"{nome_base}.pdf",
            'status': 'sucesso'
        }

    except Exception as e:
        logger.error(f"Erro ao processar servidor {servidor.get('nome', 'Desconhecido')}: {str(e)}")
        return {
            'nome': servidor.get('nome', 'Desconhecido'),
            'setor': servidor.get('setor', 'Desconhecido'),
            'erro': str(e),
            'status': 'erro'
        }

@bp_converte_setor_pdf.route('/api/setores/pdf', methods=['POST'])
def converte_setores_pdf():
    try:
        # Validação inicial
        body = request.get_json(silent=True) or {}
        setores_nomes = body.get('setores', [])
        mes_body = body.get('mes')

        # Validação dos parâmetros
        if not setores_nomes:
            return jsonify({'erro': 'Nenhum setor selecionado'}), 400
            
        if not all(isinstance(nome, str) and nome.strip() for nome in setores_nomes):
            return jsonify({'erro': 'Nomes de setores inválidos'}), 400

        try:
            validar_mes(mes_body)
        except ValueError as e:
            logger.error(f"Erro de validação: {str(e)}")
            return jsonify({'erro': str(e)}), 400

        # Processamento de datas
        try:
            data_mes = data_atual(mes_body)
            mes_por_extenso = data_mes['mes']
            mes_numerico = data_mes['mes_numerico']
            ano = data_mes['ano']
            quantidade_dias_no_mes = pega_quantidade_dias_mes(ano, mes_numerico)
        except Exception as e:
            logger.error(f"Erro no processamento de datas: {str(e)}")
            return jsonify({'erro': 'Parâmetro de data inválido'}), 400

        # Conexão com o banco e processamento
        pasta_temp = criar_pasta_temp(mes_por_extenso)
        resultados = []
        
        try:
            with closing(connect_mysql()) as conexao, closing(conexao.cursor(dictionary=True)) as cursor:
                placeholders = ','.join(['%s'] * len(setores_nomes))
                query = f"SELECT * FROM sistema_frequenciarh.funcionarios WHERE setor IN ({placeholders}) ORDER BY setor, nome"
                
                setores_nomes_upper = [nome.upper() for nome in setores_nomes]
                cursor.execute(query, tuple(setores_nomes_upper))
                servidores = cursor.fetchall()

                if not servidores:
                    return jsonify({
                        'erro': 'Nenhum servidor encontrado',
                        'setores_procurados': setores_nomes
                    }), 404

                # Processa cada servidor
                for servidor in servidores:
                    resultado = processar_servidor(
                        servidor,
                        mes_por_extenso,
                        mes_numerico,
                        ano,
                        quantidade_dias_no_mes,
                        pasta_temp
                    )
                    resultados.append(resultado)

                # Verifica se algum documento foi gerado com sucesso
                documentos_gerados = [r for r in resultados if r.get('status') == 'sucesso']
                
                if not documentos_gerados:
                    return jsonify({
                        'erro': 'Nenhum documento foi gerado com sucesso',
                        'detalhes': resultados
                    }), 500

                # Cria arquivo ZIP
                zip_path = f"{pasta_temp}.zip"
                shutil.make_archive(pasta_temp, 'zip', pasta_temp)
                
                if not os.path.exists(zip_path):
                    raise RuntimeError("Falha ao criar arquivo ZIP")

                logger.info(f"Arquivo ZIP gerado: {zip_path}")

                # Retorna o ZIP
                response = send_file(
                    zip_path,
                    as_attachment=True,
                    download_name=f"frequencias_{mes_por_extenso}_{ano}.zip",
                    mimetype='application/zip'
                )

                return response

        except Exception as e:
            logger.error(f"Erro de banco de dados: {str(e)}")
            return jsonify({'erro': 'Erro na conexão com o banco de dados'}), 500

    except Exception as e:
        logger.error(f"Erro interno: {str(e)}")
        return jsonify({'erro': f'Erro no servidor: {str(e)}'}), 500
