from flask import Blueprint, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user
import mysql.connector

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

@login_manager.user_loader
def load_user(user_id):
    cursor = conexao.cursor(dictionary=True)
    query = "SELECT id, matricula, nome, role, senha FROM usuarios WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return Usuario(result['id'], result['matricula'], result['nome'], result['role'], result['senha'])
    return None

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    matricula = data.get('matricula')
    senha = data.get('senha')

    cursor = conexao.cursor(dictionary=True)
    query = "SELECT id, matricula, nome, senha, role FROM usuarios WHERE matricula = %s"
    cursor.execute(query, (matricula,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        return jsonify({"erro": "Usuário não encontrado!"}), 404

    from werkzeug.security import check_password_hash
    if not check_password_hash(usuario_data['senha'], senha):
        return jsonify({"erro": "Senha inválida!"}), 401

    # Criar instância do usuário e realizar login
    usuario = Usuario(usuario_data['id'], usuario_data['matricula'], usuario_data['nome'], usuario_data['role'], usuario_data['senha'])
    login_user(usuario)

    return jsonify({"mensagem": "Login realizado com sucesso!", "nome": usuario.nome, "role": usuario.role}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"mensagem": "Logout realizado com sucesso!"}), 200
