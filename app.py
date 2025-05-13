from flask import Flask, jsonify, request, abort
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_migrate import Migrate
import hashlib
import os


# Create Flask app
app = Flask(__name__)

# Configure PostgreSQL URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:Tiger@localhost:5432/bookstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Set your Flask app secret key (make sure this is a long random string in production)
app.config['SECRET_KEY'] = 'your-flask-secret-key'  # This is required for Flask session and JWT signing
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'  # This is used for signing JWT tokens

db = SQLAlchemy(app)
jwt = JWTManager(app)
# Initialize the migrate object
migrate = Migrate(app, db)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password

    def __repr__(self):
        return f'<User {self.username}>'

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

# OpenTelemetry setup
def init_tracer():
    # Set up the tracer provider with a service name
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "flask-bookstore-api"})
        )
    )
    # Add a simple exporter that logs spans to the console
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )

    # Instrument Flask to collect traces
    FlaskInstrumentor().instrument_app(app)

# Initialize tracing
init_tracer()

# Hash the password directly without salt
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Check if the entered password matches the stored hash
def check_password(stored_hash: str, password: str) -> bool:
    return stored_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

# Routes
# User Registration Route
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400

    # Create a new user with hashed password
    hashed_password = hash_password(data['password'])
    new_user = User(username=data['username'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# User Login Route
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    # Find the user
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate a JWT token
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

# Get all books (requires authentication)
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre} for book in books])

# Get a specific book (requires authentication)
@app.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"id": book.id, "title": book.title, "author": book.author, "genre": book.genre})

# Add a new book (requires authentication)
@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    data = request.get_json()
    
    if 'title' not in data or 'author' not in data or 'genre' not in data:
        return jsonify({"message": "Missing title, author, or genre"}), 400
    
    new_book = Book(title=data['title'], author=data['author'], genre=data['genre'])
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added successfully!", "book": {"id": new_book.id, "title": new_book.title, "author": new_book.author, "genre": new_book.genre}}), 201

# Delete a book (requires authentication)
@app.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "Book deleted successfully"}), 200

# Start Flask server
if __name__ == '__main__':
    app.run(debug=True)
