import mysql.connector
from mysql.connector import Error

def conect():
   
    try:
        conexao = mysql.connector.connect(
            host="12.90.1.2",       # IP do servidor
            user="devop",           # Usuário do banco
            password="DEVsjc@2025", # Senha do usuário
            database="sistema_frequenciarh"  # Nome do banco de dados
        )
        if conexao.is_connected():
            print("Conexão com o banco de dados bem-sucedida!")
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Testar a conexão
if __name__ == "__main__":
    conexao = conect()
    if conexao:
        print("Conexão estabelecida com sucesso.")
        conexao.close()
    else:
        print("Falha ao estabelecer conexão.")
