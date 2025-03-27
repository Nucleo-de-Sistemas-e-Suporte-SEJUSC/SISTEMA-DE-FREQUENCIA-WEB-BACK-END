from flask_login import logout_user
from flask import Blueprint, jsonify

bp_logout= Blueprint('logout', __name__)

@bp_logout.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"mensagem": "Logout realizado com sucesso!"}), 200
