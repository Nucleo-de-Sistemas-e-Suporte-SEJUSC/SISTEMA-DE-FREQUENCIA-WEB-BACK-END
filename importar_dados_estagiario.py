import pandas as pd
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

        # Iterar sobre os registros do DataFrame e inserir no Firestore
        for _, linha in df.iterrows():
            # Usando add() para gerar um ID automático
            db.collection("estagiarios").add({
                "nome": linha["NOME"],
                "cargo": linha["CARGO"],
                "lotacao": linha["LOTACAO"],
                "horario": linha["HORARIO"],
            })

        print("Dados importados com sucesso para a coleção 'estagiarios' no Firestore!")

    except Exception as e:
        print(f"Erro ao processar o arquivo Excel ou inserir no Firestore: {e}")

# Testar a função com um arquivo Excel
if __name__ == "__main__":
    caminho_arquivo = "FREQUÊNCIAS ESTAGIÁRIO.xlsx"  # Substitua pelo caminho do seu arquivo Excel
    importar_dados_para_firestore(caminho_arquivo)
