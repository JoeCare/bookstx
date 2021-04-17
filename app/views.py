import json

from flask.views import MethodView
from .models import Book, BookSchema, db, mm
from flask import request, jsonify
import requests


# def get_books():
#     req = requests.get(
#         "https://www.googleapis.com/books/v1/volumes?q=Hobbit").json()
#     book_items = req["items"]
#     # dig_data = dict_data["items"][0]["volumeInfo"]
#     book_dict = {}
#     for book in book_items:
#         info = book["volumeInfo"]
#         imgs = info["imageLinks"]
#         book_id = book["id"]
#         title = info["title"]
#         authors = info["authors"]
#         published_date = info["publishedDate"]
#         thumbnail = imgs["thumbnail"]
#         if "categories" in info.keys():
#             categories = info["categories"]
#             print(categories)
#         # try:
#         #     categories = info["categories"]
#         #     ratings_count = info["ratingsCount"]
#         #     average_rating = info["averageRating"]
#         # except KeyError as err:
#         #     print(err.args)
#             print(book_id, title, authors, published_date, thumbnail)
book_schema = BookSchema()
books_schema = BookSchema(many=True)


def get_data_dict(books_url):
    # books_url = "https://www.googleapis.com/books/v1/volumes?q=war"
    req = requests.get(books_url).json()
    book_items = req["items"]
    # dig_data = dict_data["items"][0]["volumeInfo"]
    book_dict = {}
    for book in book_items:
        try:
            info = book["volumeInfo"]
            imgs = info["imageLinks"]
            book_dict['book_id'] = book["id"]
            book_dict['title'] = info["title"]
            # book_dict['authors'] = info["authors"]
            book_dict['authors'] = ", ".join(info["authors"])
            book_dict['published_date'] = info["publishedDate"]
            book_dict['thumbnail'] = imgs["thumbnail"]
            if "categories" in info.keys():
                book_dict['categories'] = ", ".join(info["categories"])
                # book_dict['categories'] = info["categories"]
            if "averageRating" in info.keys():
                book_dict['average_rating'] = info["averageRating"]
            if "ratingsCount" in info.keys():
                book_dict['ratings_count'] = info["ratingsCount"]
        except KeyError as e:
            print(e)
        print(1, book_dict)
        # data_to_obj = book_schema.loads(json.dumps(book_dict))
        # print(data_to_obj)
        new_book = Book(book_dict)
        db.session.add(new_book)
        # db.session.add(data_to_obj)
        db.session.commit()
    return len(book_items)

# query_strings_mapper = {
#     "sort": Book.query.order_by()
#
#     }


class BooksAPI(MethodView):

    def get(self, book_id):
        if book_id is None:
            # return a list of books
            search_queries = request.args.to_dict()
            print(search_queries)
            if search_queries:

                return f'args given!\n{search_queries}'
            else:
                books = Book.query.all()
                results = books_schema.dump(books)
                return f'All books:\n{results}'

        else:
            book = Book.query.filter_by(id=book_id).one_or_none()
            if book:
                result = BookSchema().dump(book)
                return result

    def post(self):
        """
        Create a new  record from data object passed with request
        :param:    table of which record will be created;
        instance
        class
        :return:        201 on success, 406 if instance exists
        """
        data_url = "https://www.googleapis.com/books/v1/volumes?q=Hobbit"
        instances = get_data_dict(data_url)
        # new_loc = Book(dict_data["items"][0]["volumeInfo"])
        # db.session.add(new_loc)
        # db.session.commit()
        return jsonify(
            201, f"Instanes lodaded: {instances}") # {dig_data}", dict_data)

    def delete(self, book_id):
        # delete a single book
        pass

    def put(self, book_id):
        # update a single book
        pass
