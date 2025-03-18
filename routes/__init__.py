from flask import Blueprint

# Criação do Blueprint para as rotas
bp = Blueprint('routes', __name__)

from . import buscar  