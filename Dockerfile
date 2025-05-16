FROM python:3.12.10

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean

# Instala as dependências Python aqui
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python3", "main.py"]
