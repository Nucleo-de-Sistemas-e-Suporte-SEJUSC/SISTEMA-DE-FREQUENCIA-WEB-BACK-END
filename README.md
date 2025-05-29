# SISTEMA-DE-FREQUENCIA-WEB-BACK-END

## Visão Geral

Este projeto é um sistema web para gestão de frequência de servidores e estagiários, desenvolvido em Python com Flask, integração com MySQL e geração automatizada de documentos em PDF a partir de modelos DOCX. O sistema permite cadastro, atualização, arquivamento, ativação, geração de relatórios e download de arquivos de frequência, além de controle de acesso por permissões.

---

## Funcionalidades Principais

- **Autenticação e Autorização:**  
  Login de usuários com controle de sessão e permissões por papel (admin/editor).
- **Cadastro e Gerenciamento:**  
  - Servidores (funcionários)
  - Estagiários
- **Geração de Frequência:**  
  - Geração de documentos de frequência em PDF a partir de modelos DOCX.
  - Geração individual ou em lote (por setor ou seleção múltipla).
  - Geração de arquivos ZIP com todos os PDFs do setor/mês.
- **Download e Visualização:**  
  - Download de PDFs e ZIPs.
  - Visualização de PDFs diretamente pela API.
- **Histórico de Logs:**  
  Registro de ações relevantes no sistema.
- **Controle de Status:**  
  Arquivamento e ativação de servidores e estagiários.
- **Listagem e Busca:**  
  Listagem e busca de servidores, estagiários, setores e arquivos gerados.

---

## Estrutura do Projeto

```
.
├── main.py
├── auth.py
├── conection_mysql.py
├── decorador.py
├── chave_secreta.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── setor/
├── arquivos-temporarios/
├── meuambiente/
├── routes/
│   ├── buscar_todos.py
│   ├── buscar_estagiarios.py
│   ├── buscar_setor.py
│   ├── busca_setor_estagiario.py
│   ├── criar_servidor.py
│   ├── criar_estagiario.py
│   ├── atualizar_servidores.py
│   ├── arquivar.py
│   ├── arquivar_estagiario.py
│   ├── ativar_servidor.py
│   ├── ativar_estagiario.py
│   ├── listar_pdfs.py
│   ├── listar_pdfs_estagiarios.py
│   ├── visualiza_arquivo_servidor.py
│   ├── visualiza_arquivo_estagiario.py
│   ├── visualizar_pdf.py
│   ├── send.py
│   ├── send_setores.py
│   ├── converter_setor_estagiarios.py
│   ├── converte_servidor_pdf.py
│   ├── converte_estagiario.py
│   ├── converte_setores_pdf.py
│   └── historico_logs/
│       ├── criar_historico.py
│       └── buscar_historico.py
├── utils/
│   ├── convert_to_pdf.py
│   ├── muda_texto_documento.py
│   ├── formata_datas.py
│   └── valida_ambiente_inux.py
├── validators/
│   ├── criar_servidor_validator.py
│   └── criar_estagiario_validator.py
└── ...
```

---

## Instalação

### Pré-requisitos

- Python 3.12+
- MySQL
- LibreOffice (para geração de PDF)
- Docker (opcional)

### Instalação Manual

1. Clone o repositório:
   ```sh
   git clone https://github.com/seu-usuario/SISTEMA-DE-FREQUENCIA-WEB-BACK-END.git
   cd SISTEMA-DE-FREQUENCIA-WEB-BACK-END
   ```

2. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

3. Configure o acesso ao banco de dados em [`conection_mysql.py`](conection_mysql.py).

4. Execute o servidor:
   ```sh
   python main.py
   ```

### Usando Docker

1. Construa e suba o container:
   ```sh
   docker-compose up --build
   ```

---

## Endpoints Principais

### Autenticação

- `POST /login`  
  Login de usuário.

- `POST /logout`  
  Logout do usuário autenticado.

### Servidores

- `GET /api/servidores`  
  Lista servidores ativos.

- `POST /api/criar/servidores`  
  Cria novo servidor.

- `PUT /api/servidores/<id>`  
  Atualiza servidor.

- `PATCH /api/servidores/<id>/arquivar`  
  Arquiva servidor.

- `PATCH /api/servidores/<id>/atualizar-status`  
  Ativa servidor.

### Estagiários

- `GET /api/estagiarios`  
  Lista estagiários.

- `POST /api/estagiarios`  
  Cria novo estagiário.

- `PATCH /api/estagiarios/<id>/arquivar`  
  Arquiva estagiário.

- `PATCH /api/estagiarios/<id>/atualizar-status`  
  Ativa estagiário.

### Geração e Download de Frequência

- `POST /api/servidores/pdf`  
  Gera PDFs de frequência para servidores selecionados.

- `POST /api/estagiario/pdf`  
  Gera PDFs de frequência para estagiários selecionados.

- `POST /api/setores/pdf`  
  Gera PDFs e ZIP de frequência para todos servidores de um setor.

- `POST /api/setor/estagiar/pdf`  
  Gera PDFs e ZIP de frequência para todos estagiários de um setor.

- `GET /api/servidores/pdf/download-zip/<mes>`  
  Baixa ZIP de frequência dos servidores.

- `GET /api/estagiarios/pdf/download-zip/<mes>`  
  Baixa ZIP de frequência dos estagiários.

### Visualização de Arquivos

- `GET /api/servidores/pdf/view?setor=...&mes=...&nome=...`  
  Visualiza PDF de servidor.

- `GET /api/estagiarios/pdf/view?setor=...&mes=...&nome=...`  
  Visualiza PDF de estagiário.

---

## Observações

- Os modelos de documentos devem estar presentes na raiz do projeto:  
  - `FREQUÊNCIA_MENSAL.docx`
  - `FREQUÊNCIA ESTAGIÁRIOS - MODELO.docx`
- O sistema utiliza validação de dados com Cerberus.
- O controle de permissões é feito via Flask-Login e decoradores personalizados.

---

## Licença

Este projeto é privado e de uso interno. Para uso externo, consulte o responsável pelo projeto.
