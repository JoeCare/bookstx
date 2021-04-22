import os
from flask import json, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# Globally accessible libraries
db = SQLAlchemy()
mm = Marshmallow()


def init_app():
    """Initialize the Connexion application."""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__)
    # Load application config
    env_config = os.getenv("APP_SETTINGS", "config.DevConfig")
    app.config.from_object(env_config)
    app.json_encoder = json.JSONEncoder

    # Initialize Plugins
    db.init_app(app)
    mm.init_app(app)

    with app.app_context():
        # Include our Routes/views
        from app import views
        # from app import models

        # import os
        # import psycopg2
        # DATABASE_URL = os.environ['DATABASE_URL']
        # conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)
        books_fetch_db = views.BookScrap.as_view('books-fetch')
        books_api_view = views.BooksCrudAPI.as_view('books-api')

        app.add_url_rule('/db', view_func=books_fetch_db, methods=['POST'])
        app.add_url_rule('/books', defaults={'_id': None},
                         view_func=books_api_view, methods=['GET'])
        app.add_url_rule('/books', view_func=books_api_view, methods=['POST'])
        app.add_url_rule('/books/<_id>', view_func=books_api_view,
                         methods=['GET', 'PUT', 'DELETE'])

        return app
