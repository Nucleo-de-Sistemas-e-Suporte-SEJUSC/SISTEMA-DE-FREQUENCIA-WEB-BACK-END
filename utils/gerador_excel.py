import openpyxl
from openpyxl.styles import Alignment 

def preencher_ficha_excel(template_path, dados_funcionario, caminho_saida):
    try:
        workbook = openpyxl.load_workbook(template_path)
        sheet = workbook.active

        # PARTE 1: MAPEAMENTO PARA CAMPOS ÚNICOS
        mapeamento_campos_unicos = {
            'AA7': dados_funcionario.get('matricula'), 'F13': dados_funcionario.get('nome'),
            'B19': str(dados_funcionario.get('data_nascimento', '')), 'F19': dados_funcionario.get('estado_civil'),
            'I19': dados_funcionario.get('sexo'), 'M19': dados_funcionario.get('naturalidade'),
            'R19': dados_funcionario.get('nacionalidade'), 'V19': dados_funcionario.get('carteira_profissional'),
            'B22': dados_funcionario.get('servico_militar'), 'F22': dados_funcionario.get('titulo_eleitor'),
            'I22': dados_funcionario.get('cpf'), 'M22': dados_funcionario.get('identidade'),
            'R22': dados_funcionario.get('pis'), 'V22': dados_funcionario.get('carteira_saude'),
            'F16': dados_funcionario.get('campo_mudança_nome'), 'B26': dados_funcionario.get('nome_pai'),
            'B27': dados_funcionario.get('nome_mae'), 'D30': dados_funcionario.get('endereco'),
            'B43': str(dados_funcionario.get('data_Admissao', '')), 'F43': str(dados_funcionario.get('data_posse', '')),
            'I43': dados_funcionario.get('cargo'), 'M43': dados_funcionario.get('venc_salario'),
            'I46': dados_funcionario.get('horario'), 'B46': dados_funcionario.get('desligamento'),
            'F46': str(dados_funcionario.get('inicio_atividades', '')), 'M46': str(dados_funcionario.get('descanso_semanal', '')),
        }
        
        estilo_centralizado = Alignment(horizontal='center', vertical='center')

        # Preenche e centraliza os campos únicos
        for celula_str, valor in mapeamento_campos_unicos.items():
            if valor is None or str(valor).strip() == '':
                sheet[celula_str] = "não informado"
            else:
                sheet[celula_str] = valor
            sheet[celula_str].alignment = estilo_centralizado

        # PARTE 2: LÓGICA AUTOMATIZADA PARA AS DUAS TABELAS DE BENEFICIÁRIOS
        beneficiarios = dados_funcionario.get('beneficiarios', [])
        
        # Tabela 1 (Colunas C, K, L)
        linha_inicial_1 = 34
        for i in range(7): # Para as 7 linhas da primeira tabela
            if i < len(beneficiarios):
                beneficiario = beneficiarios[i]
                sheet[f'C{linha_inicial_1 + i}'] = beneficiario.get('nome', 'não informado')
                sheet[f'K{linha_inicial_1 + i}'] = beneficiario.get('parentesco', 'não informado')
                sheet[f'L{linha_inicial_1 + i}'] = str(beneficiario.get('data_nascimento', 'não informado'))
            else: # Limpa as linhas restantes se não houver beneficiários suficientes
                sheet[f'C{linha_inicial_1 + i}'] = ""
                sheet[f'K{linha_inicial_1 + i}'] = ""
                sheet[f'L{linha_inicial_1 + i}'] = ""
        
        # Tabela 2 (Colunas P, AA, AB)
        linha_inicial_2 = 34
        # Começa a preencher a partir do 8º beneficiário (índice 7)
        beneficiarios_tabela_2 = beneficiarios[7:] 
        for i in range(7): # Para as 7 linhas da segunda tabela
            if i < len(beneficiarios_tabela_2):
                beneficiario = beneficiarios_tabela_2[i]
                sheet[f'P{linha_inicial_2 + i}'] = beneficiario.get('nome', 'não informado')
                sheet[f'AA{linha_inicial_2 + i}'] = beneficiario.get('parentesco', 'não informado')
                sheet[f'AB{linha_inicial_2 + i}'] = str(beneficiario.get('data_nascimento', 'não informado'))
            else: # Limpa as linhas restantes
                sheet[f'P{linha_inicial_2 + i}'] = ""
                sheet[f'AA{linha_inicial_2 + i}'] = ""
                sheet[f'AB{linha_inicial_2 + i}'] = ""


        workbook.save(caminho_saida)
        return True, None

    except Exception as e:
        print(f"Erro ao preencher o Excel: {e}")
        if 'celula_str' in locals():
             return False, f"Erro ao escrever na célula '{celula_str}'. Causa: {e}"
        else:
             return False, str(e)