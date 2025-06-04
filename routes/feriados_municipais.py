from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql

bp_feriados_municipais = Blueprint('bp_feriados_municipais', __name__)

@bp_feriados_municipais.route('/api/feriados-municipais', methods=['POST'])

def cadastrar_feriado_municipal():
    body = request.json or {}
    estado = body.get('estado')
    data_feriado = body.get('data')  # formato: 'YYYY-MM-DD'
    descricao = body.get('descricao', 'Feriado Municipal')

    if not estado or not data_feriado:
        return jsonify({'erro': 'Estado e data são obrigatórios'}), 400

    conexao = connect_mysql()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO feriados_municipais (estado, data, descricao) VALUES (%s, %s, %s)",
        (estado, data_feriado, descricao)
    )
    conexao.commit()
    conexao.close()
    return jsonify({'mensagem': 'Feriado municipal cadastrado com sucesso!'}), 201