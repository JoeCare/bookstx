import os
from flask import Flask

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace(
#     "://", "ql://", 1)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from app import views

# books_api_view = BooksAPI.as_view('books-api')
#
# app.add_url_rule('/books/', defaults={'book_id': None},
#                  view_func=books_api_view, methods=['GET'])
# app.add_url_rule('/books/', view_func=books_api_view, methods=['POST'])
# app.add_url_rule('/books/<book_id>', view_func=books_api_view,
#                  methods=['GET', 'PUT', 'DELETE'])
