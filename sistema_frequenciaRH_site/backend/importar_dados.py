import pandas as pd
from mysql.connector import Error
from conection import conect

def importar_dados(file_path):
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(file_path)

        # Substituir valores ausentes (NaN) por None
        df = df.where(pd.notnull(df), None)

        # Conectar ao banco de dados
        conexao = conect()
        cursor = conexao.cursor()

        # Iterar sobre os registros do DataFrame e inserir no banco
        for _, linha in df.iterrows():
            sql = """
                INSERT INTO funcionarios 
                (setor, nome, matricula, cargo, funcao, horario, entrada, saida, ferias_inicio, ferias_termino)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                linha["SETOR"],
                linha["NOME"],
                linha["MATRICULA"],
                linha["CARGO"],
                linha["FUNCAO"] if not pd.isna(linha["FUNCAO"]) else None,
                linha["HORARIO"],
                linha["ENTRADA"] if not pd.isna(linha["ENTRADA"]) else None,
                linha["SAIDA"] if not pd.isna(linha["SAIDA"]) else None,
                linha["FERIASINICIO"] if not pd.isna(linha["FERIASINICIO"]) else None,
                linha["FERIASTERMINO"] if not pd.isna(linha["FERIASTERMINO"]) else None,
            )
            cursor.execute(sql, valores)

        # Confirmar as alterações no banco de dados
        conexao.commit()
        print("Dados importados com sucesso!")

    except Error as e:
        print(f"Erro ao conectar ou inserir no banco de dados: {e}")
    except Exception as e:
        print(f"Erro ao processar o arquivo Excel: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()
            print("Conexão com o banco de dados encerrada.")



if __name__ == "__main__":
    # Substitua pelo caminho do seu arquivo Excel
    caminho_arquivo = "nome-servidores.xlsx"
    importar_dados(caminho_arquivo)