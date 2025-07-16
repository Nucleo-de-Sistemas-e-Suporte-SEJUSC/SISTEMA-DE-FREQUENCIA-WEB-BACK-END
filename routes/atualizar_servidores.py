from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required
from decorador import roles_required

bp_atualizar_servidor = Blueprint('bp_atualizar_servidor', __name__)

@bp_atualizar_servidor.route('/api/servidores/<int:id>', methods=['PATCH']) 
#@login_required
#@roles_required('admin','editor')
def atualizar_servidor(id):
    conexao = None
    cursor = None
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        body = request.json


        cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({'erro': 'Servidor não encontrado'}), 404

    
        if 'beneficiarios' in body and isinstance(body['beneficiarios'], list):
            for ben in body['beneficiarios']:
                beneficiario_id = ben.get('id')
                
           
                if beneficiario_id and ben.get('deletar') is True:
                    cursor.execute("DELETE FROM beneficiarios WHERE id = %s AND funcionario_id = %s", (beneficiario_id, id))
                
          
                elif beneficiario_id:
                    campos_ben = {k: v for k, v in ben.items() if k in ['nome', 'parentesco', 'data_nascimento']}
                    if campos_ben:
                        set_clause = ', '.join([f"{campo} = %s" for campo in campos_ben.keys()])
                        valores = list(campos_ben.values())
                        valores.append(beneficiario_id)
                        valores.append(id)
                        query_update = f"UPDATE beneficiarios SET {set_clause} WHERE id = %s AND funcionario_id = %s"
                        cursor.execute(query_update, valores)
                
          
                elif not beneficiario_id and 'nome' in ben:
                    query_insert = """
                        INSERT INTO beneficiarios (nome, parentesco, data_nascimento, funcionario_id) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query_insert, (ben.get('nome'), ben.get('parentesco'), ben.get('data_nascimento'), id))


        campos_permitidos = ['setor', 'nome', 'matricula', 'cargo', 'funcao', 'horario', 'horarioentrada', 'horariosaida', 'feriasinicio', 'feriasfinal','data_nascimento', 'sexo', 'estado_civil', 'naturalidade', 'nacionalidade', 'identidade', 'titulo_eleitor', 'cpf', 'pis', 'data_Admissao', 'endereco', 'nome_pai', 'nome_mae', 'servico_militar', 'carteira_profissional', 'data_posse', 'venc_salario', 'desligamento', 'inicio_atividades', 'descanso_semanal']
        
        campos_para_atualizar = {campo: body[campo] for campo in campos_permitidos if campo in body}

        if campos_para_atualizar:
            set_clause = ', '.join([f"{campo} = %s" for campo in campos_para_atualizar.keys()])
            valores = list(campos_para_atualizar.values())
            valores.append(id)
            query_atualizar_funcionario = f"UPDATE funcionarios SET {set_clause} WHERE id = %s"
            cursor.execute(query_atualizar_funcionario, valores)

        
        conexao.commit()
        
        return jsonify({'mensagem': 'Servidor atualizado com sucesso'}), 200

    except Exception as exception:
        if conexao:
            conexao.rollback()
        return jsonify({'erro': f'Ocorreu um erro: {str(exception)}'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()