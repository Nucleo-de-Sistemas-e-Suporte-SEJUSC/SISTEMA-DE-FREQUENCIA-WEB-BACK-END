import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_pdf(docx_path, pdf_path):
    try:
        docx_path = os.path.abspath(docx_path)
        output_dir = os.path.dirname(os.path.abspath(pdf_path))
        
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"Arquivo DOCX não encontrado: {docx_path}")
        
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Convertendo {docx_path} para PDF...")
        
        # Executa o LibreOffice em modo headless (sem interface gráfica)
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path
        ], check=True)

        # Nome esperado do PDF (LibreOffice gera com mesmo nome)
        generated_pdf = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
        
        # Renomeia se for diferente do pdf_path desejado
        if generated_pdf != os.path.abspath(pdf_path):
            os.rename(generated_pdf, pdf_path)
        
        logger.info(f"Conversão concluída com sucesso: {pdf_path}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao chamar o LibreOffice: {e}")
        return False
    except Exception as e:
        logger.error(f"Falha na conversão: {str(e)}")
        return False
