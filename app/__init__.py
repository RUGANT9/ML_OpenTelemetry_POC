from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

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

    # Set up OpenTelemetry
    init_tracer(app)

    # Register routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app

def init_tracer(app):
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({"service.name": "flask-bookstore-api"})
        )
    )
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )
    FlaskInstrumentor().instrument_app(app)
