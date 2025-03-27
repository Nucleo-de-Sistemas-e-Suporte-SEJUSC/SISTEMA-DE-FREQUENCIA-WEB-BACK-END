from functools import wraps
from flask import jsonify
from flask_login import current_user

def roles_required(*roles):
    """
    Decorador para verificar se o usuário tem um dos papéis permitidos.
    :param roles: Lista de papéis permitidos (ex: 'admin', 'editor', 'viewer').
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verifica se o usuário atual tem um dos papéis permitidos
            if current_user.role not in roles:
                return jsonify({"erro": "Permissão negada!"}), 403
            return f(*args, **kwargs)  # Executa a função original
        return decorated_function
    return decorator
