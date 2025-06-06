import shutil # 👈 Adicione esta importação no topo do seu arquivo
from flask import Blueprint, jsonify
import os

# ... (outras importações e a definição do seu blueprint)
bp_limpar_pasta_setor = Blueprint('bp_limpar_pasta_setor', __name__)

@bp_limpar_pasta_setor.route('/api/limpar/setor', methods=['DELETE'])
def limpar_pasta_setor():
    """
    Remove a pasta 'setor' e todo o seu conteúdo.
    Ideal para ser chamada antes de iniciar uma nova geração de arquivos.
    """
    pasta_alvo = 'setor'
    try:
        # Verifica se a pasta 'setor' realmente existe
        if os.path.exists(pasta_alvo):
            # shutil.rmtree() remove a pasta e tudo que há dentro dela
            shutil.rmtree(pasta_alvo)
            print(f"INFO: Pasta '{pasta_alvo}' limpa com sucesso.")
            return jsonify({'status': 'sucesso', 'mensagem': f"A pasta '{pasta_alvo}' foi limpa com sucesso."}), 200
        else:
            # Se a pasta não existe, não há nada a fazer.
            print(f"INFO: Pasta '{pasta_alvo}' não encontrada, nenhuma ação foi necessária.")
            return jsonify({'status': 'info', 'mensagem': f"A pasta '{pasta_alvo}' não existia."}), 200
            
    except Exception as e:
        # Captura erros inesperados (ex: problemas de permissão)
        print(f"ERRO: Falha ao limpar a pasta '{pasta_alvo}'. Erro: {e}")
        return jsonify({'erro': f"Falha ao limpar a pasta: {str(e)}"}), 500