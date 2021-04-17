from app import app
from app.views import BooksCrudAPI, BookScrap

books_fetch_db = BookScrap.as_view('books-fetch')
books_api_view = BooksCrudAPI.as_view('books-api')

app.add_url_rule('/books', defaults={'_id': None},
                 view_func=books_api_view, methods=['GET'])
app.add_url_rule('/books', view_func=books_api_view, methods=['POST'])
app.add_url_rule('/db', view_func=books_fetch_db, methods=['POST'])
app.add_url_rule('/books/<_id>', view_func=books_api_view,
                 methods=['GET', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run()
