from flask import Blueprint, jsonify, request
from mysql.connector import Error
from conection_mysql import connect_mysql
from flask_login import login_required  
from decorador import roles_required   
from flask_cors import cross_origin

bp_buscar_setor = Blueprint('bp_buscar_setor', __name__)

@bp_buscar_setor.route("/api/buscar_setor", methods=["GET"])

def buscar_setor():

    token = request.cookies.get('food')
    try:
       
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        consulta_setores = """
                SELECT setor, COUNT(*) AS quantidade
                FROM funcionarios
                WHERE status != 'arquivado'
                GROUP BY setor
            """
        cursor.execute(consulta_setores)
            
        
        setores_quantidade = cursor.fetchall()
            
        return jsonify({"setores": setores_quantidade}), 200
        
    except Error as e:
       
        return jsonify({"erro": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    
    finally:
       
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()