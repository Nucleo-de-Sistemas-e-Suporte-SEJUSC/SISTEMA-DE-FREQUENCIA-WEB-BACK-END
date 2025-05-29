from functools import wraps
from flask import jsonify
from flask_login import current_user

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = getattr(current_user, 'role', [])
            if isinstance(user_roles, str):
                user_roles = [user_roles]
            if not any(role in user_roles for role in roles):
                return jsonify({'erro': 'Acesso negado: Voce nao tem permissão para acessar o conteudo !'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
