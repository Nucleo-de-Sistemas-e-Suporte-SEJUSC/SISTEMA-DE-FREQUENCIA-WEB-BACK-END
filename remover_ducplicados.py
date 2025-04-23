import mysql.connector

def remover_duplicados():
    try:
        conexao = mysql.connector.connect(
            host="12.90.1.2",
            user="devop",
            password="DEVsjc@2025",
            database="sistema_frequenciarh"
        )
        cursor = conexao.cursor()
        
        # Script SQL para remover duplicados
        query = """
            DELETE t1
            FROM funcionarios t1
            INNER JOIN funcionarios t2
            ON t1.nome = t2.nome AND t1.setor = t2.setor
            WHERE t1.id > t2.id;
        """
        
        cursor.execute(query)
        conexao.commit()
        print("Duplicados removidos com sucesso!")
    
    except mysql.connector.Error as err:
        print(f"Erro: {err}")
    
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Executa a função
remover_duplicados()
