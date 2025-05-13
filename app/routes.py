from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from app import db
from app.models import User, Book
from app.utils import hash_password, check_password

bp = Blueprint('api', __name__)

# User Registration Route
@bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = hash_password(data['password'])
    new_user = User(username=data['username'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# User Login Route
@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

# Get all books (requires authentication)
@bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "genre": book.genre} for book in books])

# Get a specific book (requires authentication)
@bp.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"id": book.id, "title": book.title, "author": book.author, "genre": book.genre})

# Add a new book (requires authentication)
@bp.route('/books', methods=['POST'])
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
@bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "Book deleted successfully"}), 200
