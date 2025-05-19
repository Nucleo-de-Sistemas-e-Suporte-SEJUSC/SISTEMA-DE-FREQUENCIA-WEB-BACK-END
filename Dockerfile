# Usa uma imagem oficial do Python
FROM python:3.12.3-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements.txt inicialmente (melhor para cache)
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Expõe a porta 8000 (ou outra usada pelo seu app)
EXPOSE 8000

# Comando para iniciar o app
CMD ["python3", "main.py"]
