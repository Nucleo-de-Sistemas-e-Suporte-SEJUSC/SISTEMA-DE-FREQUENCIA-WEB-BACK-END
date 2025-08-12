from validators.criar_servidor_validator import validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required, current_user
from decorador import roles_required

bp_criar_servidor = Blueprint('bp_criar_servidor', __name__)

@bp_criar_servidor.route('/api/criar/servidores', methods=['POST'])
@login_required
@roles_required('admin','editor')
def criar_servidor():
    conexao = None
    cursor = None
    try:
        body = request.get_json()
        if not body:
            return jsonify({'erro': 'JSON não enviado ou malformado'}), 400

        validate = validator.validate(body)
        if not validate:
            print("Erros de validação:", validator.errors)
            return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400

        try:
            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)
        except Error as db_err:
            return jsonify({'erro': 'Erro ao conectar ao banco de dados', 'mensagem': str(db_err)}), 500

        setor = body.get('setor')
        nome = body.get('nome')
        matricula = body.get('matricula')
        cargo = body.get('cargo')
        horario = body.get('horario')
        horarioentrada = body.get('entrada')
        horariosaida = body.get('saida')
        dataNascimento = body.get('data_nascimento')
        sexo = body.get('sexo')
        estadoCivil = body.get('estado_civil')
        naturalidade = body.get('naturalidade')
        nacionalidade = body.get('nacionalidade')
        identidade = body.get('identidade')
        tituloEleitor = body.get('titulo_eleitor')
        cpf = body.get('cpf')
        pis = body.get('pis')
        dataAdmissao = body.get('data_admissao')

       
        endereco = body.get('endereco')
        nome_pai = body.get('nome_pai')
        nome_mae = body.get('nome_mae')
        servico_militar = body.get('servico_militar')
        carteira_profissional = body.get('carteira_profissional')
        data_posse = body.get('data_posse')

      
        try:
            verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE nome = %s"
            cursor.execute(verifica_se_servidor_existe, (nome,))
            if cursor.fetchone():
                return jsonify({'erro': 'Servidor já cadastrado'}), 409
        except Error as db_err:
            return jsonify({'erro': 'Erro ao consultar duplicidade', 'mensagem': str(db_err)}), 500

    
        try:
            criar_dados_servidor = """
                INSERT INTO funcionarios (
                    setor, nome, matricula, cargo, horario, horarioentrada, horariosaida, 
                    data_Nascimento, sexo, estado_Civil, naturalidade, nacionalidade, 
                    identidade, titulo_Eleitor, cpf, pis, data_Admissao,
                    endereco, nome_pai, nome_mae, servico_militar, carteira_profissional, data_posse, cadastrado_por
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(criar_dados_servidor, (
                setor, nome, matricula, cargo, horario, horarioentrada, horariosaida,
                dataNascimento, sexo, estadoCivil, naturalidade,
                nacionalidade, identidade, tituloEleitor, cpf, pis, dataAdmissao,
                endereco, nome_pai, nome_mae, servico_militar, carteira_profissional, data_posse, current_user.id
            ))
            conexao.commit()
        except Error as db_err:
            print(db_err)
            return jsonify({'erro': 'Erro ao inserir servidor', 'mensagem': str(db_err)}), 500

      
        dados_retornados = {
            "id": cursor.lastrowid,
            "setor": setor, "nome": nome, "matricula": matricula, "cargo": cargo,
            "data_admissao": dataAdmissao, "horario": horario, "entrada": horarioentrada,
            "saida": horariosaida, "data_nascimento": dataNascimento, "sexo": sexo,
            'estado_civil': estadoCivil, "naturalidade": naturalidade, "nacionalidade": nacionalidade,
            "identidade": identidade, "titulo_eleitor": tituloEleitor, "cpf": cpf, "pis": pis,
      
            "endereco": endereco, "nome_pai": nome_pai, "nome_mae": nome_mae, 
            "servico_militar": servico_militar, "carteira_profissional": carteira_profissional, 
            "data_posse": data_posse
        }
        return jsonify({'servidor': dados_retornados}), 201

    except Exception as exception:
        return jsonify({'erro': 'Erro inesperado', 'mensagem': str(exception)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()