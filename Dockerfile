# Baixar uma imagem oficial baseada em Windows
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Instala o Python 3.12.3
RUN powershell -Command \
    $ProgressPreference = 'SilentlyContinue'; \
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe" -OutFile "C:\python-installer.exe"; \
    Start-Process -Wait -FilePath "C:\python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"; \
    Remove-Item -Path "C:\python-installer.exe" -Force

# Atualiza o pip e configura o ambiente
RUN python -m pip install --upgrade pip

# Define o diretório de trabalho
WORKDIR C:/app

# Copia os requirements primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt waitress

# Copia o restante da aplicação
COPY . .

# Expõe a porta
EXPOSE 3000

# Comando para rodar a aplicação
CMD ["python", "-m", "waitress", "--port=3000", "main:app"]