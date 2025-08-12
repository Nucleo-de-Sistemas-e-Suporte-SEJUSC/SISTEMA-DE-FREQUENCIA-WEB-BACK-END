from flask import jsonify, Blueprint
from datetime import timedelta
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required, current_user
from decorador import roles_required   

bp_ultimos_cadastros = Blueprint('bp_ultimos_cadastros', __name__)

def timedelta_to_str(td):
    """Converte timedelta em string no formato HH:MM:SS"""
    if td is None:
        return None
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@bp_ultimos_cadastros.route('/api/ultimos-cadastros', methods=['GET'])
@login_required
@roles_required('admin','editor')
def buscar_ultimos_cadastros():
    """
    Busca os 10 últimos servidores e estagiários cadastrados no sistema
    Retorna apenas registros ativos (não arquivados)
    """
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)

        # Buscar últimos 10 servidores cadastrados pelo usuário logado
        query_servidores = """
            SELECT 
                f.id, f.nome, f.matricula, f.setor, f.cargo, 
                DATE_FORMAT(f.data_Admissao, '%d/%m/%Y') as data_admissao_formatada,
                u.nome as cadastrado_por_nome,
                'servidor' as tipo_cadastro
            FROM funcionarios f
            LEFT JOIN usuarios u ON f.cadastrado_por = u.id
            WHERE (f.status != 'arquivado' OR f.status IS NULL) 
            AND f.cadastrado_por = %s
            ORDER BY f.id DESC 
            LIMIT 10
        """
        cursor.execute(query_servidores, (current_user.id,))
        ultimos_servidores = cursor.fetchall()

        # # Buscar últimos 10 estagiários cadastrados (se tiver coluna cadastrado_por, filtrar por usuário)
        # query_estagiarios = """
        #     SELECT 
        #         id, nome, setor, cargo,
        #         'estagiario' as tipo_cadastro
        #     FROM estagiarios 
        #     WHERE status != 'arquivado' OR status IS NULL
        #     ORDER BY id DESC 
        #     LIMIT 10
        # """
        # cursor.execute(query_estagiarios)
        # ultimos_estagiarios = cursor.fetchall()

        # Processar dados dos servidores para converter timedelta
        for servidor in ultimos_servidores:
            for key, value in servidor.items():
                if isinstance(value, timedelta):
                    servidor[key] = timedelta_to_str(value)

        # # Processar dados dos estagiários para converter timedelta
        # for estagiario in ultimos_estagiarios:
        #     for key, value in estagiario.items():
        #         if isinstance(value, timedelta):
        #             estagiario[key] = timedelta_to_str(value)

        # Combinar e ordenar todos os cadastros por ID (mais recente primeiro)
        todos_cadastros = []
        
        # Adicionar servidores com identificação
        for servidor in ultimos_servidores:
            todos_cadastros.append({
                'id': servidor['id'],
                'nome': servidor['nome'],
                'setor': servidor['setor'],
                'cargo': servidor['cargo'],
                'matricula': servidor.get('matricula', 'N/A'),
                'data_admissao': servidor.get('data_admissao_formatada', 'N/A'),
                'tipo': 'Servidor'
            })

        # # Adicionar estagiários com identificação
        # for estagiario in ultimos_estagiarios:
        #     todos_cadastros.append({
        #         'id': estagiario['id'],
        #         'nome': estagiario['nome'],
        #         'setor': estagiario['setor'],
        #         'cargo': estagiario['cargo'],
        #         'matricula': 'N/A',  # Estagiários não têm matrícula
        #         'data_admissao': 'N/A',  # Estagiários não têm data de admissão
        #         'tipo': 'Estagiário'
        #     })

        # Ordenar todos por ID decrescente (mais recentes primeiro) e pegar apenas os 15 mais recentes
        todos_cadastros.sort(key=lambda x: x['id'], reverse=True)
        ultimos_15_cadastros = todos_cadastros[:15]

        cursor.close()
        conexao.close()

        return jsonify({
            "ultimos_cadastros": ultimos_15_cadastros,
            "total": len(ultimos_15_cadastros),
            "usuario_logado": current_user.nome if current_user.is_authenticated else "Não identificado"
        }), 200

    except Error as e:
        return jsonify({
            "erro": f"Erro ao conectar ao banco de dados: {str(e)}"
        }), 500
    except Exception as exception:
        return jsonify({
            "erro": f"Erro interno do servidor: {str(exception)}"
        }), 500
