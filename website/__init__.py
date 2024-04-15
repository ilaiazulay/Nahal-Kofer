import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate

from website.mqtt_client import stop_mqtt
from .scheduler import setup_scheduler
from flask_mail import Mail, Message

load_dotenv()

db = SQLAlchemy()

mail = Mail()


def create_app():
    app = Flask(__name__)
    #
    # @app.teardown_appcontext
    # def stop_mqtt_client(exception=None):
    #     # Stop the MQTT client when the app shuts down
    #     stop_mqtt()

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getenv("DB_NAME")}'
    app.config['MAIL_SERVER'] = 'smtp.zoho.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
    mail.init_app(app)

    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    db.init_app(app)
    # migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


# Make mail accessible
def get_mail():
    return mail

