from sqlalchemy import Table, Column, Integer, String

# Conectar ao banco de dados
connection = mysql.connector.connect(
            host="12.90.1.2",         # Endereço do servidor MySQL (ou IP interno da intranet)
            user="devop",             # Usuário do banco de dados
            password="DEVsjc@2025",   # Senha do banco de dados
            database="sistema_frequenciarh"  # Nome do banco de dados
        )

# Definir a tabela 'usuarios'
usuarios = Table(
    'usuarios',
    Column('id', Integer, primary_key=True),
    Column('matricula', String(50), nullable=False),
    Column('nome', String(100), nullable=False)
)

# Criar a tabela no banco de dados
metadata.create_all(engine)
print("Tabela 'usuarios' criada com sucesso.")
