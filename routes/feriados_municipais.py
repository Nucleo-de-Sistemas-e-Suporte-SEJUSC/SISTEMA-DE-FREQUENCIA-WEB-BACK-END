from flask import Blueprint, request, jsonify
from conection_mysql import connect_mysql

bp_feriados_municipais = Blueprint('bp_feriados_municipais', __name__)

@bp_feriados_municipais.route('/api/feriados-municipais', methods=['POST'])

def cadastrar_feriado_municipal():
    body = request.json or {}
    estado = body.get('estado')
    data_feriado = body.get('data')  # formato: 'YYYY-MM-DD'
    descricao = body.get('descricao')
    
    # Trata o campo como booleano (1 para sim, 0 para não)
    ponto_facultativo = 1 if body.get('ponto_facultativo') else 0

    if not estado or not data_feriado:
        return jsonify({'erro': 'Estado e data são obrigatórios'}), 400

    # Define uma descrição padrão caso não seja informada
    if not descricao:
        descricao = 'Ponto Facultativo' if ponto_facultativo else 'Feriado Municipal'

    conexao = connect_mysql()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO feriados_municipais (estado, data, descricao, ponto_facultativo) VALUES (%s, %s, %s, %s)",
        (estado, data_feriado, descricao, ponto_facultativo)
    )
    conexao.commit()
    conexao.close()
    return jsonify({'mensagem': 'Data cadastrada com sucesso!'}), 201