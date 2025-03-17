from flask import jsonify, request
from datetime import timedelta
from conection import conect
from mysql.connector import Error
from . import bp  # Importa o Blueprint

def timedelta_to_str(td):
    """Converte timedelta em string no formato HH:MM:SS"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@bp.route("/api/servidores", methods=["GET"])
def buscar_servidores():
    try:
        conexao = conect()
        cursor = conexao.cursor(dictionary=True)

        # Verifica se o parâmetro `listar_setores` foi enviado
        listar_setores = request.args.get("listar_setores", "false").lower() == "true"
        if listar_setores:
            # Consulta para listar todos os setores distintos
            consulta_setores = "SELECT DISTINCT setor FROM funcionarios"
            cursor.execute(consulta_setores)
            setores = [row["setor"] for row in cursor.fetchall()]
            return jsonify({"setores": setores}), 200

        # Consulta padrão para buscar servidores
        consulta = "SELECT * FROM funcionarios WHERE 1=1"
        parametros = []

        # Filtros opcionais
        setor = request.args.get("setor")
        if setor:
            consulta += " AND setor = %s"
            parametros.append(setor)

        nome = request.args.get("nome")
        if nome:
            consulta += " AND nome LIKE %s"
            parametros.append(f"%{nome}%")

        # Executa a consulta
        cursor.execute(consulta, tuple(parametros))
        servidores = cursor.fetchall()

        if len(servidores) == 0:
            conexao.close()
            return jsonify({"erro": "Nenhum servidor encontrado"}), 404
            
        # Converte campos timedelta em string
        for servidor in servidores:
            for key, value in servidor.items():
                if isinstance(value, timedelta):
                    servidor[key] = timedelta_to_str(value)

        return jsonify({"servidores": servidores}), 200

    except Error as e:
        return jsonify({"erro": f"Erro ao conectar ou buscar dados no banco de dados: {str(e)}"}), 500

    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()
