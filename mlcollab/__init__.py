from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from mlcollab.config import Config
from flask_ckeditor import CKEditor


db = SQLAlchemy()
login_manager = LoginManager()
hash_controller = Bcrypt()
ckeditor = CKEditor()

# Dictionary to hold information about Netron servers
netron_servers = {}


def init_application(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = "VERY VERY SECRET"

    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    hash_controller.init_app(app)
    ckeditor.init_app(app)

    # Import Blueprints
    from mlcollab.public.routes import public
    from mlcollab.admin.routes import admin
    from mlcollab.errors.routes import error
    from mlcollab.api.routes import api

    # Register Blueprints
    app.register_blueprint(public)
    app.register_blueprint(admin)
    app.register_blueprint(error)
    app.register_blueprint(api)

    return app
