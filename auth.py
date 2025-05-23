from flask import Blueprint, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import mysql.connector

auth_bp = Blueprint("auth", __name__)

# 🔹 Criando o login_manager DENTRO do auth.py
login_manager = LoginManager()

def get_db_connection():
    return mysql.connector.connect(
        host="12.90.1.2",
        user="devop",
        password="DEVsjc@2025",
        database="sistema_frequenciarh"
    )

class Usuario(UserMixin):
    def __init__(self, id, matricula, nome, role,cargo):
        self.id = id
        self.matricula = matricula
        self.nome = nome
        self.role = role
        self.cargo = cargo

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT id, matricula, nome, role, cargo FROM usuarios WHERE id = %s", (user_id,))
    usuario_data = cursor.fetchone()

    cursor.close()
    conexao.close()

    if usuario_data:
        return Usuario(usuario_data["id"], usuario_data["matricula"], usuario_data["nome"], usuario_data["role"], usuario_data["cargo"])
    return None

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    matricula = data.get("matricula")
    senha = data.get("senha")

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT id, matricula, nome, senha, role, cargo FROM usuarios WHERE matricula = %s", (matricula,))
    usuario_data = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not usuario_data:
        return jsonify({"erro": "Usuário não encontrado!"}), 404
    print("Usuário não encontrado!")

    if usuario_data["senha"] != senha:
        return jsonify({"erro": "Senha inválida!"}), 401

    usuario = Usuario(usuario_data["id"], usuario_data["matricula"], usuario_data["nome"], usuario_data["role"], usuario_data["cargo"])
    login_user(usuario, remember=True)

    return jsonify({"mensagem": "Login realizado com sucesso!", "nome": usuario.nome, "role": usuario.role, "cargo": usuario.cargo}), 200

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"mensagem": "Logout realizado com sucesso!"}), 200
