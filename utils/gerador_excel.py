import openpyxl
from openpyxl.styles import Alignment 

def preencher_ficha_excel(template_path, dados_funcionario, caminho_saida):
    try:
        workbook = openpyxl.load_workbook(template_path)
        sheet = workbook.active

        mapeamento_celulas = {
            # --- Bloco Superior ---
            'AA7': dados_funcionario.get('matricula'),
            'F13': dados_funcionario.get('nome'),

            # --- Linha de Dados Pessoais 1 ---
            'B19': str(dados_funcionario.get('data_nascimento', '')),
            'F19': dados_funcionario.get('estado_civil'),
            'I19': dados_funcionario.get('sexo'),
            'M19': dados_funcionario.get('naturalidade'),
            'R19': dados_funcionario.get('nacionalidade'),
            'V19': dados_funcionario.get('carteira_profissional'),

            # --- Linha de Dados Pessoais 2 ---
            'B22': dados_funcionario.get('servico_militar'),
            'F22': dados_funcionario.get('titulo_eleitor'),
            'I22': dados_funcionario.get('cpf'),
            'M22': dados_funcionario.get('identidade'),
            'R22': dados_funcionario.get('pis'),
            'V22': dados_funcionario.get('carteira_saude'), # Campo não está no banco
            'F16': dados_funcionario.get('campo_mudança_nome'),

            # --- Bloco de Filiação ---
            'B26': dados_funcionario.get('nome_pai'),
            'B27': dados_funcionario.get('nome_mae'),
            'C34': dados_funcionario.get('campo_nome_beneficiario'), # Campo não está no banco
            'C35': dados_funcionario.get('campo_nome_beneficiario'),
            'C36': dados_funcionario.get('campo_nome_beneficiario'),
            'C37': dados_funcionario.get('campo_nome_beneficiario'),
            'C38': dados_funcionario.get('campo_nome_beneficiario'),
            'C39': dados_funcionario.get('campo_nome_beneficiario'),
            'C40': dados_funcionario.get('campo_nome_beneficiario'),
            'K34': dados_funcionario.get('campo_parentesco'),
            'K35': dados_funcionario.get('campo_parentesco'),
            'K36': dados_funcionario.get('campo_parentesco'),
            'K37': dados_funcionario.get('campo_parentesco'),
            'K38': dados_funcionario.get('campo_parentesco'),
            'K39': dados_funcionario.get('campo_parentesco'),
            'K40': dados_funcionario.get('campo_parentesco'),
            'L34': dados_funcionario.get('campo_nascimento'),
            'L35': dados_funcionario.get('campo_nascimento'),
            'L36': dados_funcionario.get('campo_nascimento'),
            'L37': dados_funcionario.get('campo_nascimento'),
            'L38': dados_funcionario.get('campo_nascimento'),
            'L39': dados_funcionario.get('campo_nascimento'),
            'L40': dados_funcionario.get('campo_nascimento'),
            
            
            
            'P34': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P35': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P36': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P37': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P38': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P39': dados_funcionario.get('campo_nome_beneficiario_2'),
            'P40': dados_funcionario.get('campo_nome_beneficiario_2'),
            'K35': dados_funcionario.get('campo_nome_beneficiario_2'),
            'AA34': dados_funcionario.get('campo_parentesco_2'),
            'AA35': dados_funcionario.get('campo_parentesco_2'),
            'AA36': dados_funcionario.get('campo_parentesco_2'),
            'AA37': dados_funcionario.get('campo_parentesco_2'),
            'AA38': dados_funcionario.get('campo_parentesco_2'),
            'AA39': dados_funcionario.get('campo_parentesco_2'),
            'AA40': dados_funcionario.get('campo_parentesco_2'),
            'AB34': dados_funcionario.get('campo_nascimento_2'),
            'AB35': dados_funcionario.get('campo_nascimento_2'),
            'AB36': dados_funcionario.get('campo_nascimento_2'),
            'AB37': dados_funcionario.get('campo_nascimento_2'),
            'AB38': dados_funcionario.get('campo_nascimento_2'),
            'AB39': dados_funcionario.get('campo_nascimento_2'),
            'AB40': dados_funcionario.get('campo_nascimento_2'),
            # --- Bloco de Endereço ---
            'D30': dados_funcionario.get('endereco'), # Adicione a célula correta aqui

            # --- Bloco de Dados Funcionais Inferior ---
            'B43': str(dados_funcionario.get('data_Admissao', '')),
            'F43': str(dados_funcionario.get('data_posse', '')),
            'I43': dados_funcionario.get('cargo'),
            'M43': dados_funcionario.get('venc_salario'), # Este campo pode estar faltando no seu banco
            'I46': dados_funcionario.get('horario'),
            'B46': dados_funcionario.get('desligamento'),
            'F46': str(dados_funcionario.get('inicio_atividades', '')),
            'M46': str(dados_funcionario.get('descanso_semanal', '')),
        }
        
        estilo_centralizado = Alignment(horizontal='center', vertical='center')

        # --- LÓGICA ATUALIZADA AQUI ---
        # Itera sobre os dados e preenche as células
        for celula_str, valor in mapeamento_celulas.items():
            # Verifica se o valor é nulo, uma string vazia, ou uma string que só contém espaços
            if valor is None or str(valor).strip() == '':
                sheet[celula_str] = "não informado"
            else:
                sheet[celula_str] = valor
        sheet[celula_str].alignment = estilo_centralizado

        workbook.save(caminho_saida)
        return True, None

    except Exception as e:
        print(f"Erro ao preencher o Excel: {e}")
        if 'celula_str' in locals():
             return False, f"Erro ao escrever na célula '{celula_str}'. Causa: {e}"
        else:
             return False, str(e)