import openpyxl
from openpyxl.styles import Alignment 
from datetime import datetime, date


def formatar_data_por_extenso(data_obj):
    """
    Converte um objeto de data para uma string em português por extenso.
    Exemplo: date(2025, 7, 14) -> "14 de julho de 2025"
    """
    if not isinstance(data_obj, (datetime, date)):
        return "data não informada"
    
    meses = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    
    dia = data_obj.day
    mes = meses[data_obj.month - 1] # Pega o nome do mês (índice 0-11)
    ano = data_obj.year
    
    return f"{dia} de {mes} de {ano}"

def preencher_ficha_excel(template_path, dados_funcionario, caminho_saida):
    """
    Preenche a Ficha Funcional completa a partir de um template Excel (.xlsx),
    incluindo múltiplas abas e formatações específicas.

    :param template_path: Caminho para o template .xlsx.
    :param dados_funcionario: Dicionário com os dados do funcionário e a lista de beneficiários.
    :param caminho_saida: Onde salvar o novo arquivo .xlsx preenchido.
    :return: Tupla (sucesso_boolean, erro_mensagem_string)
    """
    try:
        workbook = openpyxl.load_workbook(template_path)
        
        # --- ESTILOS DE ALINHAMENTO ---
        estilo_centralizado = Alignment(horizontal='center', vertical='center', wrap_text=True)
        estilo_esquerda = Alignment(horizontal='left', vertical='center', wrap_text=True)

        # ======================================================================
        # --- ABA 1: FRENTE ---
        # ======================================================================
        
        # Seleciona a primeira aba pelo nome. Ajuste se o nome for diferente.
        sheet_frente = workbook["FRENTE"]

        # Mapeamento dos campos únicos da primeira página
        mapeamento_frente = {
            'AA7': dados_funcionario.get('matricula'), 'F13': dados_funcionario.get('nome'),
            'B19': dados_funcionario.get('data_nascimento'), 'F19': dados_funcionario.get('estado_civil'),
            'I19': dados_funcionario.get('sexo'), 'M19': dados_funcionario.get('naturalidade'),
            'R19': dados_funcionario.get('nacionalidade'), 'V19': dados_funcionario.get('carteira_profissional'),
            'B22': dados_funcionario.get('servico_militar'), 'F22': dados_funcionario.get('titulo_eleitor'),
            'I22': dados_funcionario.get('cpf'), 'M22': dados_funcionario.get('identidade'),
            'R22': dados_funcionario.get('pis'), 'V22': dados_funcionario.get('carteira_saude'),
            'F16': dados_funcionario.get('campo_mudança_nome'), 'B26': dados_funcionario.get('nome_pai'),
            'B27': dados_funcionario.get('nome_mae'), 'D30': dados_funcionario.get('endereco'),
            'B43': dados_funcionario.get('data_Admissao'), 'F43': dados_funcionario.get('data_posse'),
            'I43': dados_funcionario.get('cargo'), 'M43': dados_funcionario.get('venc_salario'),
            'I46': dados_funcionario.get('horario'), 'B46': dados_funcionario.get('desligamento'),
            'F46': dados_funcionario.get('inicio_atividades'), 'M46': dados_funcionario.get('descanso_semanal'),
        }
        
        celulas_de_data_frente = ['B19', 'B43', 'F43', 'F46']

        # Preenche os campos únicos da aba "FRENTE"
        for celula_str, valor in mapeamento_frente.items():
            valor_final = valor
            if celula_str in celulas_de_data_frente and isinstance(valor, (datetime, date)):
                valor_final = valor.strftime('%d/%m/%Y')
            
            if valor_final is None or str(valor_final).strip() == '':
                sheet_frente[celula_str] = "não informado"
            else:
                sheet_frente[celula_str] = str(valor_final)
            
            sheet_frente[celula_str].alignment = estilo_esquerda if celula_str in ['F13', 'F16'] else estilo_centralizado

        # Preenche as duas tabelas de beneficiários na aba "FRENTE"
        beneficiarios = dados_funcionario.get('beneficiarios', [])
        tabelas_beneficiarios = [
            {'colunas': {'nome': 'C', 'parentesco': 'K', 'nascimento': 'L'}, 'start_index': 0},
            {'colunas': {'nome': 'P', 'parentesco': 'AA', 'nascimento': 'AB'}, 'start_index': 7}
        ]
        
        for tabela in tabelas_beneficiarios:
            linha_inicial = 34
            max_linhas = 7
            for i in range(max_linhas):
                indice_beneficiario = tabela['start_index'] + i
                
                if indice_beneficiario < len(beneficiarios):
                    ben = beneficiarios[indice_beneficiario]
                    data_nasc_ben = ben.get('data_nascimento')
                    data_formatada_ben = data_nasc_ben.strftime('%d/%m/%Y') if isinstance(data_nasc_ben, (datetime, date)) else "não informado"

                    sheet_frente[f"{tabela['colunas']['nome']}{linha_inicial + i}"] = ben.get('nome', 'não informado')
                    sheet_frente[f"{tabela['colunas']['parentesco']}{linha_inicial + i}"] = ben.get('parentesco', 'não informado')
                    sheet_frente[f"{tabela['colunas']['nascimento']}{linha_inicial + i}"] = data_formatada_ben
                else:
                    sheet_frente[f"{tabela['colunas']['nome']}{linha_inicial + i}"] = ""
                    sheet_frente[f"{tabela['colunas']['parentesco']}{linha_inicial + i}"] = ""
                    sheet_frente[f"{tabela['colunas']['nascimento']}{linha_inicial + i}"] = ""


        # ======================================================================
        # --- ABA 2: OUTRAS ANOTAÇÕES ---
        # ======================================================================
        
        # Seleciona a segunda aba pelo nome. Ajuste se o nome for diferente.
        sheet_anotacoes = workbook["OUTRAS ANOTAÇÕES"]
        
        data_admissao_extenso = formatar_data_por_extenso(dados_funcionario.get('data_Admissao'))
        # Supondo que você tenha um campo 'data_publicacao' no seu banco
        data_publicacao_extenso = formatar_data_por_extenso(dados_funcionario.get('data_publicacao'))

        # IMPORTANTE: Use as células corretas (canto superior esquerdo)
        mapeamento_anotacoes = {
            'A2': dados_funcionario.get('nome'),      # Exemplo
            'B4': dados_funcionario.get('cargo'),      # Exemplo
            'C3': data_publicacao_extenso.upper(),            # Exemplo
            'G3': data_admissao_extenso.upper(),              # Exemplo
        }

        # --- LÓGICA DE PREENCHIMENTO E ALINHAMENTO CORRIGIDA ---
        for celula_str, valor in mapeamento_anotacoes.items():
            if valor is None or str(valor).strip() == '':
                 sheet_anotacoes[celula_str] = "não informado"
            else:
                 sheet_anotacoes[celula_str] = str(valor)
            
            # Aplica o estilo de alinhamento desejado. 
            # Para a maioria dos textos longos, o alinhamento à esquerda com quebra de linha é o ideal.
            sheet_anotacoes[celula_str].alignment = estilo_esquerda

        workbook.save(caminho_saida)
        return True, None

    except KeyError as e:
        print(f"Erro: A aba com o nome '{e}' não foi encontrada.")
        return False, f"Aba '{e}' não encontrada."
    except Exception as e:
        print(f"Erro ao preencher o Excel: {e}")
        if 'celula_str' in locals():
             return False, f"Erro ao escrever na célula '{celula_str}'. Causa: {e}"
        else:
             return False, str(e)