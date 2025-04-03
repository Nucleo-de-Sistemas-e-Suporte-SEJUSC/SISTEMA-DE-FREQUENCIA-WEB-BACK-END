from flask import Blueprint, jsonify, request
from mysql.connector import Error
from conection_mysql import connect_mysql
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required   # Importa o decorador personalizado
from flask_cors import cross_origin

bp_buscar_setor_estagiario = Blueprint('bp_buscar_setor_estagiario', __name__)

@bp_buscar_setor_estagiario.route("/api/setor/estagiarios", methods=["GET"])
# @cross_origin(supports_credentials=True)  # Permite o compartilhamento de credenciais
# @roles_required('admin','editor')
def buscar_setor_estagiario():

    token = request.cookies.get('food')
    try:
        # Conexão com o banco de dados
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        consulta_setores = """
                SELECT lotacao, COUNT(*) AS quantidade, id
                FROM estagiarios 
                GROUP BY lotacao
            """
        cursor.execute(consulta_setores)
            
        # Recupera os resultados da consulta
        setores_quantidade = cursor.fetchall()
            
        # Retorna os resultados em formato JSON
        return jsonify({"setores": setores_quantidade}), 200
        
    except Error as e:
        # Tratamento de erro no banco de dados
        return jsonify({"erro": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    
    finally:
        # Fecha a conexão com o banco de dados, se aberta
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()