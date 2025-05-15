import shutil
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def valida_ambiente_pdf_linux(pasta_teste='setor/teste_pdf'):
    erros = []

    # Verifica se o LibreOffice está disponível no PATH
    caminho_libreoffice = shutil.which("libreoffice")
    if not caminho_libreoffice:
        erros.append("LibreOffice não está instalado ou não está no PATH.")
    else:
        logger.info(f"LibreOffice encontrado em: {caminho_libreoffice}")

    # Verifica se consegue criar e escrever em uma pasta
    try:
        os.makedirs(pasta_teste, exist_ok=True)
        teste_arquivo = os.path.join(pasta_teste, 'teste.txt')
        with open(teste_arquivo, 'w') as f:
            f.write("Teste de escrita.")
        os.remove(teste_arquivo)
        logger.info(f"Permissões de escrita OK na pasta: {pasta_teste}")
    except Exception as e:
        erros.append(f"Erro ao escrever na pasta {pasta_teste}: {str(e)}")

    # Retorna resultado
    if erros:
        for erro in erros:
            logger.error(erro)
        return False, erros
    else:
        logger.info("Ambiente validado com sucesso para geração de PDFs com LibreOffice.")
        return True, []
