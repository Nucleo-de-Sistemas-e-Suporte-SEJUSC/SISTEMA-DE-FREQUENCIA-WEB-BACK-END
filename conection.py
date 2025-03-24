import firebase_admin
from firebase_admin import credentials, firestore

# Função para conectar ao Firestore
def conect_firestore():
    try:
        # Caminho para o arquivo JSON da conta de serviço (substitua pelo caminho correto)
        service_account_key_path = "C:/Users/70352867213/Documents/chave-firebase/gestao-rh-9d04d-firebase-adminsdk-fbsvc-b5477928e6.json"
        
        # Inicializar Firebase Admin SDK
        if not firebase_admin._apps:  # Verifica se o Firebase já foi inicializado
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)

        # Inicializar Firestore
        db = firestore.client()
        print("Conexão com o Firestore bem-sucedida!")
        return db
    except Exception as e:
        print(f"Erro ao conectar ao Firestore: {e}")
        return None

# Teste da conexão (somente para depuração)
if __name__ == "__main__":
    db = conect_firestore()
    if db:
        print("Conexão com Firestore estabelecida com sucesso.")
    else:
        print("Falha ao estabelecer conexão com Firestore.")
