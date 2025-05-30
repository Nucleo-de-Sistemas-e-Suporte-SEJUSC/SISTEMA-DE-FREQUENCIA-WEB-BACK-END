from validators.criar_servidor_validator import validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required
from decorador import roles_required

bp_criar_servidor = Blueprint('bp_criar_servidor', __name__)

@bp_criar_servidor.route('/api/criar/servidores', methods=['POST'])
#@login_required
#@roles_required('admin','editor')
def criar_servidor():
    conexao = None
    cursor = None
    try:
        # Validação do JSON recebido
        body = request.get_json()
        if not body:
            return jsonify({'erro': 'JSON não enviado ou malformado'}), 400

        validate = validator.validate(body)
        print("Erros de validação:", validator.errors)

        if not validate:
            return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400

        # Conexão com o banco de dados
        try:
            conexao = connect_mysql()
            cursor = conexao.cursor(dictionary=True)
        except Error as db_err:
            return jsonify({'erro': 'Erro ao conectar ao banco de dados', 'mensagem': str(db_err)}), 500

        # Extração dos campos
        setor = body.get('setor')
        nome = body.get('nome')
        matricula = body.get('matricula')
        cargo = body.get('cargo')
        #funcao = body.get('funcao')
        horario = body.get('horario')
        horarioentrada = body.get('entrada')
        horariosaida = body.get('saida')
        feriasinicio = body.get('feriasinicio')
        feriasfinal = body.get('feriasfinal')
        dataNascimento = body.get('data_nascimento')
        sexo = body.get('sexo')
        estadoCivil = body.get('estado_civil')
        naturalidade = body.get('naturalidade')
        nacionalidade = body.get('nacionalidade')
        identidade = body.get('identidade')
        tituloEleitor = body.get('titulo_eleitor')
        cpf = body.get('cpf')
        pis = body.get('pis')
        rg = body.get('rg')
        #dataAdmissao = body.get('data_admissao')

        # Verifica duplicidade
        try:
            verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE nome = %s"
            cursor.execute(verifica_se_servidor_existe, (nome,))
            servidor = cursor.fetchone()
            if servidor:
                return jsonify({'erro': 'Servidor já cadastrado'}), 409
        except Error as db_err:
            return jsonify({'erro': 'Erro ao consultar duplicidade', 'mensagem': str(db_err)}), 500

        # Inserção
        try:
            criar_dados_servidor = """
                INSERT INTO funcionarios (setor, nome, matricula, cargo, horario, horarioentrada, horariosaida, feriasinicio, feriasfinal, data_Nascimento, sexo, estado_Civil, naturalidade, nacionalidade, identidade, titulo_Eleitor, cpf, pis,rg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
            """
            cursor.execute(criar_dados_servidor, (
                setor, nome, matricula, cargo, horario, horarioentrada, horariosaida,
                feriasinicio, feriasfinal, dataNascimento, sexo, estadoCivil, naturalidade,
                nacionalidade, identidade, tituloEleitor, cpf, pis, rg
            ))
            conexao.commit()
        except Error as db_err:
            print(db_err)
            return jsonify({'erro': 'Erro ao inserir servidor', 'mensagem': str(db_err)}), 500

        dados_retornados = {
            "id": cursor.lastrowid,
            "setor": setor,
            "nome": nome,
            "matricula": matricula,
            "cargo": cargo,
            #"data_admissao": dataAdmissao,
            #"funcao": funcao,
            "horario": horario,
            "entrada": horarioentrada,
            "saida": horariosaida,
            "feriasinicio": feriasinicio,
            "feriastermino": feriasfinal,
            "data_nascimento": dataNascimento,
            "sexo": sexo,
            'estado_civil': estadoCivil,
            "naturalidade": naturalidade,
            "nacionalidade": nacionalidade,
            "identidade": identidade,
            "titulo_eleitor": tituloEleitor,
            "cpf": cpf,
            "pis": pis,
            "rg": rg
        }
        return jsonify({'servidor': dados_retornados}), 201

    except Exception as exception:
        return jsonify({'erro': 'Erro inesperado', 'mensagem': str(exception)}), 500

    finally:
        # Garante fechamento do cursor e conexão mesmo em caso de erro
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
