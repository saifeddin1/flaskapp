from flask import abort
from flask_login import current_user


def role_required(role):
    def wrapper(func):
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)  # Forbidden
            return func(*args, **kwargs)
        return decorated_view
    return wrapper
