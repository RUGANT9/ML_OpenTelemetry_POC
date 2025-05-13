from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configurations for the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:Tiger@localhost:5432/bookstore'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-flask-secret-key'
    app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app
