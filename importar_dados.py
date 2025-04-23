import pandas as pd
from datetime import datetime, timedelta
from conection import conect_firestore

def importar_dados_para_firestore(file_path):
    try:
        # Estabelecer conexão com Firestore
        db = conect_firestore()
        if not db:
            raise Exception("Falha ao conectar ao Firestore.")

        # Ler o arquivo Excel
        df = pd.read_excel(file_path)

        # Substituir valores ausentes (NaN) por None
        df = df.where(pd.notnull(df), None)

        # Função para converter Timedelta em datetime ou string
        def converter_timedelta_para_hora(td):
            if isinstance(td, pd.Timedelta):
                total_segundos = td.total_seconds()
                horas = int(total_segundos // 3600)
                minutos = int((total_segundos % 3600) // 60)
                segundos = int(total_segundos % 60)
                return f"{horas:02}:{minutos:02}:{segundos:02}"  # Retorna como string no formato HH:MM:SS
            return None

        # Iterar sobre os registros do DataFrame e inserir no Firestore
        for _, linha in df.iterrows():
            horarioentrada = converter_timedelta_para_hora(linha["HORARIOENTRADA"])
            horariosaida = converter_timedelta_para_hora(linha["HORARIOSAIDA"])

            # Inserir dados no Firestore
            db.collection("funcionarios").add({
                "setor": linha["SETOR"],
                "nome": linha["NOME"],
                "matricula": linha["MATRICULA"],
                "cargo": linha["CARGO"],
                "funcao": linha["FUNCAO"] if not pd.isna(linha["FUNCAO"]) else None,
                "horarioentrada": horarioentrada,
                "horariosaida": horariosaida,
                "feriasinicio": linha["FERIASINICIO"] if not pd.isna(linha["FERIASINICIO"]) else None,
                "feriasfinal": linha["FERIASFINAL"] if not pd.isna(linha["FERIASFINAL"]) else None,
            })

        print("Dados importados com sucesso para o Firestore!")

    except Exception as e:
        print(f"Erro ao processar o arquivo Excel ou inserir no Firestore: {e}")

# Testar a função com um arquivo Excel
if __name__ == "__main__":
    caminho_arquivo = "nome-servidores.xlsx"  # Substitua pelo caminho do seu arquivo Excel
    importar_dados_para_firestore(caminho_arquivo)
