from flask import Flask, jsonify
from mysql.connector import Error
from routes import bp as routes_bp
from routes.criar_servidor import bp_criar_servidor
from routes.converte_servidor_pdf import bp_converte_servidor_pdf
from routes.converte_setores_pdf import bp_converte_setor_pdf
from flask_cors import CORS
from routes.atualizar_servidores import bp_atualizar_servidor
from routes.arquivar import bp_arquivar_servidor
from routes.ativar_servidor import bp_ativar_servidor_status
from routes.buscar_arquivados import bp_buscar_servidores_arquivados
from routes.buscar_estagiarios import bp_buscar_estagiarios
from routes.buscar_setor import bp_buscar_setor
from routes.listar_pdfs import bp_listar_pdfs
from routes.visualizar_pdf import bp_visualizar_pdf
from routes.busca_setor_estagiario import bp_buscar_setor_estagiario
from routes.historico_logs.criar_historico import bp_criar_historico
from routes.historico_logs.buscar_historico import bp_buscar_historico
from routes.converte_estagiario import bp_converte_estagiario_pdf
from routes.send import bp_send_servidor_pdf
from routes.send_setores import bp_send_setor_pdf
from routes.visualiza_arquivo_servidor import bp_visualiza_pdf_arquivo
from routes.converter_setor_estagiarios import bp_converte_setor_estagiario_pdf
from routes.visualiza_arquivo_estagiario import bp_visualiza_pdf_arquivo_estagiario
from routes.listar_pdfs_estagiarios import bp_listar_pdfs_estagiarios
from routes.criar_estagiario import bp_criar_estagiario
from routes.arquivar_estagiario import bp_arquivar_estagiario
from routes.ativar_estagiario   import bp_ativar_estagiario
from routes.send_varios_setores import bp_send_varios_setores_pdf
from routes.send_varios_setores_estagiario import bp_send_varios_setores_estagiarios_pdf
from auth import auth_bp, login_manager  # ✅ Importação correta
import os

app = Flask(__name__)
# Configura CORS uma única vez com os dois domínios permitidos
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://localhost:8080",
    #"http://12.90.4.88:8080",
    "http://12.90.4.98:8080",
])

# Adiciona os cabeçalhos extras corretamente (sem sobrescrever)
@app.after_request
def after_request(response):
    origin = response.headers.get('Access-Control-Allow-Origin')
    if origin:
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

login_manager.init_app(app)
app.secret_key = 'sa3fab861d0da4efd62c6f2aff0649b5e'

# Registro dos Blueprints
app.register_blueprint(routes_bp)
app.register_blueprint(bp_criar_servidor)
app.register_blueprint(bp_converte_servidor_pdf)
app.register_blueprint(bp_converte_setor_pdf)
app.register_blueprint(bp_atualizar_servidor)
app.register_blueprint(bp_arquivar_servidor)
app.register_blueprint(bp_ativar_servidor_status)
app.register_blueprint(bp_buscar_servidores_arquivados)
app.register_blueprint(bp_buscar_estagiarios)
app.register_blueprint(bp_buscar_setor)
app.register_blueprint(bp_listar_pdfs)
app.register_blueprint(bp_visualizar_pdf)
app.register_blueprint(bp_criar_historico)
app.register_blueprint(bp_buscar_historico)
app.register_blueprint(bp_converte_estagiario_pdf)
app.register_blueprint(auth_bp)
app.register_blueprint(bp_send_servidor_pdf)
app.register_blueprint(bp_send_setor_pdf)
app.register_blueprint(bp_visualiza_pdf_arquivo)
app.register_blueprint(bp_buscar_setor_estagiario)
app.register_blueprint(bp_converte_setor_estagiario_pdf)
app.register_blueprint(bp_visualiza_pdf_arquivo_estagiario)
app.register_blueprint(bp_listar_pdfs_estagiarios)
app.register_blueprint(bp_criar_estagiario)
app.register_blueprint(bp_arquivar_estagiario)
app.register_blueprint(bp_ativar_estagiario)
app.register_blueprint(bp_send_varios_setores_pdf)
app.register_blueprint(bp_send_varios_setores_estagiarios_pdf)
@app.route("/")
def home():
    return 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
