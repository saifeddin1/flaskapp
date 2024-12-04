from routes.auth_routes import auth_routes
from routes.analysis_routes import analysis_routes
from routes.report_routes import report_routes
from routes.operation_routes import operation_routes
from routes.main_routes import main_routes
from flask import Flask
from flask_mail import Mail
from models import db
from config import Config
from flask_login import LoginManager
from models import User
# Initialisation de Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Création des tables dans la base de données
with app.app_context():
    db.create_all()

# Blueprints à ajouter (routes principales, etc.)

app.register_blueprint(main_routes)
app.register_blueprint(operation_routes, url_prefix='/operations')
app.register_blueprint(report_routes, url_prefix='/reports')
# Vérifiez cet enregistrement
app.register_blueprint(analysis_routes, url_prefix='/analysis')
# Set a URL prefix for auth routes
app.register_blueprint(auth_routes, url_prefix='/auth')


if __name__ == '__main__':
    app.run(debug=True)
