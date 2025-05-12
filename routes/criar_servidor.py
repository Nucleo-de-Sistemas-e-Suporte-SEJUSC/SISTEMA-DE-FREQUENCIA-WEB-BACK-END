from validators.criar_servidor_validator import validator
from cerberus import Validator
from flask import jsonify, request, Blueprint
from conection_mysql import connect_mysql
from mysql.connector import Error
from flask_login import login_required  # Importa diretamente do Flask-Login
from decorador import roles_required 
# Importa o decorador personalizado


bp_criar_servidor = Blueprint('bp_criar_servidor', __name__)


@bp_criar_servidor.route('/api/servidores', methods=['POST'])
#@login_required
#@roles_required('admin','editor')
def criar_servidor():
    try:
        conexao = connect_mysql()
        cursor = conexao.cursor(dictionary=True)
        body = request.json
        validate = validator.validate(body)
        
        if validate == False:
            return jsonify({'erro': 'Dados inválidos', 'mensagem': validator.errors}), 400


        setor = body.get('setor')
        nome = body.get('nome')                                                                 
        matricula = body.get('matricula')
        cargo = body.get('cargo')
        funcao = body.get('funcao')
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

        verifica_se_servidor_existe = "SELECT * FROM funcionarios WHERE nome = %s"
        cursor.execute(verifica_se_servidor_existe, (nome,))
        servidor = cursor.fetchone()

        if servidor:
            conexao.close()
            return jsonify({'erro': 'Servidor já cadastrado'}), 409

        criar_dados_servidor = """
            INSERT INTO funcionarios (setor, nome, matricula, cargo, funcao, horario, horarioentrada, horariosaida, feriasinicio, feriasfinal, data_Nascimento, sexo, estado_Civil, naturalidade, nacionalidade, identidade, titulo_Eleitor, cpf, pis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
        """
        cursor.execute(criar_dados_servidor, (setor, nome, matricula, cargo, funcao, horario,horarioentrada, horariosaida, feriasinicio, feriasfinal,dataNascimento, sexo, estadoCivil, naturalidade, nacionalidade, identidade, tituloEleitor, cpf, pis))
        conexao.commit()
        conexao.close()
        
        dados_retornados = {
            "id": cursor.lastrowid,
            "setor": setor,
            "nome": nome,
            "matricula": matricula,
            "cargo": cargo,
            "funcao": funcao,
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
            "pis": pis
        } 

        return jsonify({'servidor': dados_retornados}), 201
    except Exception as exception:
        return jsonify({'erro': f'Erro ao conectar ao banco de dados: {str(exception)}'}), 500

