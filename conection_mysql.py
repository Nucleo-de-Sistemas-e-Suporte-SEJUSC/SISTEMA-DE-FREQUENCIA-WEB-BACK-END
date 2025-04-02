import mysql.connector
from mysql.connector import Error

def connect_mysql():
    try:
        # Configurações do banco de dados MySQL (substitua pelos seus valores)
        connection = mysql.connector.connect(
            #host="12.90.1.2",         # Endereço do servidor MySQL (ou IP interno da intranet)
            #user="devop",             # Usuário do banco de dados
            #password="DEVsjc@2025",   # Senha do banco de dados
            #database="sistema_frequenciarh"  # Nome do banco de dados
            
            host="127.0.0.1",         # Endereço do servidor MySQL (ou IP interno da intranet)
            user="root",             # Usuário do banco de dados
            password="",   # Senha do banco de dados
            database="sistema_frequenciarh"  # Nome do banco de dados
        )
        
        if connection.is_connected():
            print("Conexão com o MySQL bem-sucedida!")
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


# Testar conexão com MySQL
db_mysql = connect_mysql()
if db_mysql:
    print("Conexão com MySQL estabelecida com sucesso.")
    db_mysql.close()  # Fechar conexão após teste
else:
    print("Falha ao estabelecer conexão com MySQL.")
