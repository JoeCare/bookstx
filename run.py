from app import app
from app.views import BooksAPI

books_api_view = BooksAPI.as_view('books-api')

app.add_url_rule('/books', defaults={'book_id': None},
                 view_func=books_api_view, methods=['GET'])
app.add_url_rule('/books', view_func=books_api_view, methods=['POST'])
app.add_url_rule('/db', view_func=books_api_view, methods=['POST'])
app.add_url_rule('/books/<book_id>', view_func=books_api_view,
                 methods=['GET', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run()
