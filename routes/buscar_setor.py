from flask import Blueprint, jsonify, request
from mysql.connector import Error
from conection_mysql import connect_mysql
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required   # Importa o decorador personalizado


bp_buscar_setor = Blueprint('bp_buscar_setor', __name__)

@bp_buscar_setor.route("/api/buscar_setor", methods=["GET"])
# @login_required
# @roles_required('admin','editor')
def buscar_setor():
    try:
        # Conexão com o banco de dados
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        consulta_setores = """
                SELECT setor, COUNT(*) AS quantidade, id
                FROM funcionarios 
                GROUP BY setor
            """
        cursor.execute(consulta_setores)
            
            # Recupera os resultados da consulta
        setores_quantidade = cursor.fetchall()
            
            # Retorna os resultados em formato JSON
        return jsonify({"setores": setores_quantidade}), 200
        
        # Verifica se o parâmetro listar_setor foi passado na requisição
        # listar_setor = request.args.get("listar_setor", "false").lower() == "true"
        # if listar_setor:
        #     # Consulta para contar pessoas por setor
        #     consulta_setores = """
        #         SELECT setor, COUNT(*) AS quantidade 
        #         FROM funcionarios 
        #         GROUP BY setor
        #     """
        #     cursor.execute(consulta_setores)
            
        #     # Recupera os resultados da consulta
        #     setores_quantidade = cursor.fetchall()
            
        #     # Retorna os resultados em formato JSON
        #     return jsonify({"setores": setores_quantidade}), 200
        
        # # Caso o parâmetro não seja passado, retorna uma mensagem padrão
        # return jsonify({"mensagem": "Parâmetro listar_setor não informado ou inválido."}), 400
    
    except Error as e:
        # Tratamento de erro no banco de dados
        return jsonify({"erro": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    
    finally:
        # Fecha a conexão com o banco de dados, se aberta
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()