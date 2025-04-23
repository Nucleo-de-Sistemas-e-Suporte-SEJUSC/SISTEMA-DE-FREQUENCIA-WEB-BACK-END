import os
import pythoncom
import win32com.client
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def word_application():
    pythoncom.CoInitialize()
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        yield word
    finally:
        if word:
            try:
                word.Quit()
            except Exception as e:
                logger.error(f"Erro ao fechar Word: {str(e)}")
        pythoncom.CoUninitialize()

def convert_to_pdf(docx_path, pdf_path):
    doc = None
    try:
        # Verifica e normaliza caminhos
        docx_path = os.path.abspath(docx_path)
        pdf_path = os.path.abspath(pdf_path)
        
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"Arquivo DOCX não encontrado: {docx_path}")
        
        # Cria diretório de destino se não existir
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        with word_application() as word:
            logger.info(f"Convertendo {docx_path} para {pdf_path}")
            
            # Abre o documento
            doc = word.Documents.Open(docx_path)
            
            # Configuração para PDF (FileFormat=17)
            doc.SaveAs(pdf_path, FileFormat=17)
            
            logger.info(f"Conversão concluída com sucesso: {pdf_path}")
            return True
            
    except Exception as e:
        logger.error(f"Falha na conversão: {str(e)}")
        # Tenta fechar o documento se estiver aberto
        if doc:
            try:
                doc.Close(False)
            except:
                pass
        return False
    finally:
        # Garante que o documento seja fechado
        if doc:
            try:
                doc.Close(False)
            except:
                pass