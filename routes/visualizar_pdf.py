import os
from flask import Flask, send_from_directory, abort, Blueprint
from urllib.parse import unquote
from unicodedata import normalize

app = Flask(__name__)
app.config['PDF_BASE'] = r'C:\Users\02122287225\Documents\SISTEMA-DE-FREQUENCIA-WEB-BACK-END\setor'
bp_visualizar_pdf = Blueprint('bp_visualizar_pdf', __name__)

def normalizar_nome(nome):
    """Converte para formato do sistema de arquivos (remove acentos, espaços vira _)"""
    nome_sem_acentos = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome_sem_acentos.replace(' ', '_').upper()

@bp_visualizar_pdf.route('/api/pdf/<setor>/<mes>/<nome_servidor>/<nome_arquivo>')
def visualizar_pdf(setor, mes, nome_servidor, nome_arquivo):
    try:
        # Construa o caminho conforme sua estrutura real
        caminho_pasta = os.path.join(
            app.config['PDF_BASE'],
            f"setor-{setor}",
            "servidor",
            mes,
            nome_servidor.replace(' ', '_').replace('Ç', 'C').replace('Ã', 'A')
        )
        arquivo = nome_arquivo.replace(' ', '_').replace('Ç', 'C').replace('Ã', 'A')
        
        print(f"Procurando em: {caminho_pasta}")
        print(f"Arquivos na pasta: {os.listdir(caminho_pasta)}")  # 👈 Mostra o que existe
        
        return send_from_directory(
            directory=caminho_pasta,
            path=arquivo,
            as_attachment=False
        )
    except Exception as e:
        print(f"Erro completo: {str(e)}")  # 👈 Mostra o erro real
        abort(404)