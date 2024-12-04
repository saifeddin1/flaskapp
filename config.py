import os


class Config:
    # Base de données SQLite (modifiable pour PostgreSQL ou MySQL)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///viticulture.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour les sessions Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

    # Configuration pour les emails
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # Remplacez avec votre email
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'saifeddinmatoui4@gmail.com')
    # Remplacez avec votre mot de passe
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'vCA4T21KsmZDtO5U')
    MAIL_DEFAULT_SENDER = 'your-email@example.com'  # Remplacez par votre email
