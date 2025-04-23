from flask import Blueprint, request, jsonify
from flask_login import LoginManager, UserMixin, login_user
import mysql.connector
from flask import make_response

# Configuração do Flask-Login
login_manager = LoginManager()

# Blueprint para as rotas de autenticação
auth_bp = Blueprint('auth', __name__)

# Conexão com o banco de dados MySQL
conexao = mysql.connector.connect(
    host="12.90.1.2",
    user="devop",
    password="DEVsjc@2025",
    database="sistema_frequenciarh"
)

# Classe de Usuário para Flask-Login
class Usuario(UserMixin):
    def __init__(self, id, matricula, nome, role, senha):
        self.id = id
        self.matricula = matricula
        self.nome = nome
        self.role = role
        self.senha = senha
   
    def get_id(self):
        return self.id



@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    matricula = data.get('matricula')
    senha = data.get('senha')

    # Conexão com o banco de dados
    cursor = conexao.cursor(dictionary=True)
    query = "SELECT id, matricula, nome, senha, role FROM usuarios WHERE matricula = %s"
    cursor.execute(query, (matricula,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        return jsonify({"erro": "Usuário não encontrado!"}), 404

    if usuario_data['senha'] != senha:
        return jsonify({"erro": "Senha inválida!"}), 401

    # Criar instância do usuário e realizar login
    usuario = Usuario(usuario_data['id'], usuario_data['matricula'], usuario_data['nome'], usuario_data['role'], usuario_data['senha'])
    login_user(usuario)

    # Configurar o cookie de autenticação
    response = make_response(jsonify({"mensagem": "Login realizado com sucesso!", "nome": usuario.nome, "role": usuario.role}), 200)
    response.set_cookie('food', 'jwt-token', httponly=True, secure=False, samesite='None')

    return response


@login_manager.user_loader
def load_user(user_id):
    cursor = conexao.cursor(dictionary=True)
    query = "SELECT id, matricula, nome, senha, role FROM usuarios WHERE id = %s"
    cursor.execute(query, (user_id,))
    usuario_data = cursor.fetchone()

    if usuario_data:
        return Usuario(usuario_data['id'], usuario_data['matricula'], usuario_data['nome'], usuario_data['role'], usuario_data['senha'])

    return None
