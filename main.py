from flask import Flask, jsonify, request
from mysql.connector import Error
from routes import bp as routes_bp  # Importa o Blueprint definido em routes/__init__.py
from routes.criar_servidor import  bp_criar_servidor
from routes.converte_servidor_pdf import bp_converte_servidor_pdf
from routes.converte_setores_pdf import bp_converte_setor_pdf
from flask_cors import CORS 
from routes.atualizar_servidores import bp_atualizar_servidor
from routes.arquivar import bp_arquivar_servidor
from routes.ativar_servidor import bp_atualizar_servidor_status
from routes.buscar_arquivados import bp_buscar_servidores_arquivados
from routes.buscar_estagiarios import bp_buscar_estagiarios


app = Flask(__name__)
CORS(app)  # Habilita o CORS na aplicação

app.register_blueprint(routes_bp) # busca todos os servidores
app.register_blueprint(bp_criar_servidor) # cria um servidor
app.register_blueprint(bp_converte_servidor_pdf) # converte um servidor em pdf
app.register_blueprint(bp_converte_setor_pdf) #convert um setor em pdf
#app.register_blueprint(bp_deletar_servidor)
app.register_blueprint(bp_atualizar_servidor) # atualiza um servidor
app.register_blueprint(bp_arquivar_servidor)
app.register_blueprint(bp_atualizar_servidor_status)
app.register_blueprint(bp_buscar_servidores_arquivados)
app.register_blueprint(bp_buscar_estagiarios)


@app.route("/")
def home():
    return "Bem vindo ao sistema de frequencia do rh!"

app.run(host= "0.0.0.0", port=3000, debug=True)
