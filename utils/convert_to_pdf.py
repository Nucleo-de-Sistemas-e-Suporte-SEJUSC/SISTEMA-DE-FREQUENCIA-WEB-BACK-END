import os
import pythoncom 
import win32com.client
from docx import Document

def convert_to_pdf(docx_path, pdf_path):
    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.visible = False
        
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"O arquivo '{docx_path}' não foi encontrado.")
        
        doc = word.Documents.Open(docx_path)
        
        doc.SaveAs(pdf_path, FileFormat=17)
        
        doc.Close()
        word.Quit()
        
    except Exception as e:
        raise Exception(f"Erro ao converter para PDF: {str(e)}")
