import os
from conection import conect  # Certifique-se de que o módulo 'conection' está no mesmo diretório ou no PYTHONPATH

def recuperar_template(template_id, caminho_destino):
    """Recupera um arquivo do banco de dados e salva localmente"""
    conexao = conect()
    if not conexao:
        print("Erro: Não foi possível conectar ao banco.")
        return

    cursor = conexao.cursor(dictionary=True)
    try:
        # Busca o template no banco pelo ID
        cursor.execute("SELECT nome, conteudo FROM templates WHERE id = %s", (template_id,))
        template = cursor.fetchone()

        if not template:
            print("Erro: Template não encontrado.")
            return

        # Verifica se o diretório de destino existe; cria se não existir
        if not os.path.exists(caminho_destino):
            os.makedirs(caminho_destino, exist_ok=True)

        # Salva o conteúdo binário em um arquivo local
        caminho_arquivo = os.path.join(caminho_destino, template["nome"])
        with open(caminho_arquivo, "wb") as file:
            file.write(template["conteudo"])

        print(f"Arquivo '{template['nome']}' recuperado com sucesso e salvo em '{caminho_arquivo}'!")
    except Exception as e:
        print(f"Erro ao recuperar template: {e}")
    finally:
        cursor.close()
        conexao.close()

# Testando a função
recuperar_template(1, r'C:\Users\02122287225\Documents\favoritos-sejusc\SEJUSC')