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
        
        setor_especifico = request.args.get('setor')
        
        if setor_especifico:

            consulta_ids = """
                SELECT id, nome, setor, cargo
                FROM funcionarios
                WHERE status != 'arquivado' AND setor = %s
                ORDER BY nome
            """
            cursor.execute(consulta_ids, (setor_especifico,))
            funcionarios = cursor.fetchall()
            
            ids_selecionados = []
            for funcionario in funcionarios:
                ids_selecionados.append(funcionario['id'])
            
            return jsonify({
                "setor": setor_especifico,
                "ids_selecionados": ids_selecionados,
                "funcionarios": funcionarios,
                "total": len(funcionarios)
            }), 200
        else:
            consulta_setores = """
                SELECT setor, COUNT(*) AS quantidade, GROUP_CONCAT(id) AS ids
                FROM funcionarios
                WHERE status != 'arquivado'
                GROUP BY setor
            """
            cursor.execute(consulta_setores)
            setores_quantidade = cursor.fetchall()

            for setor in setores_quantidade:
                if setor['ids']:
                    setor['ids'] = [int(id) for id in setor['ids'].split(',')]
                else:
                    setor['ids'] = []
            
            return jsonify({"setores": setores_quantidade}), 200
        
    except Error as e:
       
        return jsonify({"erro": f"Erro ao conectar ao banco de dados: {str(e)}"}), 500
    
    finally:
       
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()