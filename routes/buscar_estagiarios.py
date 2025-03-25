from flask import Blueprint, jsonify, request
from mysql.connector import Error
from conection_mysql import connect_mysql

# Definir o Blueprint
bp_buscar_estagiarios = Blueprint('bp_buscar_estagiarios', __name__)

@bp_buscar_estagiarios.route("/api/estagiarios", methods=["GET"])
def buscar_estagiarios():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Consulta padrão para buscar estagiários
        consulta = "SELECT * FROM estagiarios WHERE 1=1"
        parametros = []

        # Filtros opcionais
        nome = request.args.get("nome")
        if nome:
            consulta += " AND nome LIKE %s"
            parametros.append(f"%{nome}%")
            
        setor = request.args.get("setor")
        if setor:
            consulta += " AND setor = %s"
            parametros.append(setor)

        # Executa a consulta
        cursor.execute(consulta, tuple(parametros))
        estagiarios = cursor.fetchall()

        if len(estagiarios) == 0:
            return jsonify({"estagiarios": []}), 200

        return jsonify({"estagiarios": estagiarios}), 200

    except Error as e:
        return jsonify({"erro": f"Erro ao buscar estagiários: {str(e)}"}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexao' in locals() and conexao.is_connected():
            conexao.close()
