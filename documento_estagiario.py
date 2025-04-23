import os
from conection_mysql import connect_mysql

def enviar_template(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print('Erro: Arquivo não encontrado.')
        return

    # Verifica se o arquivo é um .docx
    if not caminho_arquivo.endswith('.docx'):
        print('Erro: Arquivo não é um documento do Word.')
        return

    with open(caminho_arquivo, "rb") as file:
        conteudo = file.read()

    conexao = connect_mysql()  # Corrigido: Nome correto da função
    if not conexao: 
        print("Erro: Não foi possível conectar ao banco.")
        return

    cursor = conexao.cursor()
    try:
        nome_arquivo = os.path.basename(caminho_arquivo)
        cursor.execute(
            "INSERT INTO template (nome, conteudo) VALUES (%s, %s)",
            (nome_arquivo, conteudo)
        )
        conexao.commit()
        print(f"Arquivo '{nome_arquivo}' enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()
            
caminho = r"C:\\Users\\70352867213\\projetos_sejusc\\SISTEMA-DE-FREQUENCIA-WEB-BACK-END\\FREQUÊNCIA-ESTAGIÁRIOS-MODELO.docx"
enviar_template(caminho)
