from flask.views import MethodView, View
from .models import Book, BookSchema, db, mm
from flask import request, jsonify
import requests, re


# def get_books():
#     req = requests.get(
#         "https://www.googleapis.com/books/v1/volumes?q=Hobbit").json()
#     book_items = req["items"]
#     # dig_data = dict_data["items"][0]["volumeInfo"]
#     book_dict = {}
#     for book in book_items:
#         info = book["volumeInfo"]
#         imgs = info["imageLinks"]
#         _id = book["id"]
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
#             print(_id, title, authors, published_date, thumbnail)
book_schema = BookSchema()
books_schema = BookSchema(many=True)
                          # exclude=['ratings_count', 'average_rating'])


class BookScrap(MethodView):

    def post(self):
        books_url = "https://www.googleapis.com/books/v1/volumes?q=Hobbit"
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
                # book_dict['publisher'] = info["publisher"]
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
            # print(book_dict)
            # data_to_obj = book_schema.loads(json.dumps(book_dict))
            # print(data_to_obj)
            new_book = Book(book_dict)
            db.session.add(new_book)
            # db.session.add(data_to_obj)
            db.session.commit()
        return jsonify(
            201, f"Instances loaded: {len(book_items)}")

# query_strings_mapper = {
#     "sort": Book.query.order_by()
#
#     }


class BooksCrudAPI(MethodView):

    def get(self, _id):
        """
        Return list of all records at /books or particular one at /books/<id>
        :param _id:                 main ID number of record in our database
        :return single record:      retrieved according to given _id
        :return collection:         return all records of /books resource
        """
        if _id is None:
            query_string = request.args.to_dict()
            queries = ['sort', 'filter', 'authors',
                       'published_date', 'categories']
            if query_string:
                if re.compile('|'.join(queries), re.IGNORECASE).search(
                        str(query_string)):
                    same = set(query_string).intersection(set(queries))

                    return jsonify({"?": query_string},
                                   {400: 'Missing or invalid parameters!'})
                return jsonify({400: 'Parameters required!'},
                               {"Possible queries": queries})
            else:
                # return list without custom queries
                books = Book.query.all()
                results = books_schema.dump(books)
                return jsonify(results)
        else:
            # return single record according to _id
            book = Book.query.filter_by(id=_id).one_or_none()
            if book:
                result = book_schema.dump(book)
                return jsonify(result)

    def post(self):
        """
        Create a new  record from data object passed with request
        :param:    table of which record will be created;
        instance
        class
        :return:        201 on success, 406 if instance exists
        """
        data_url = "https://www.googleapis.com/books/v1/volumes?q=Hobbit"
        # instances = get_data_dict(data_url)
        # new_loc = Book(dict_data["items"][0]["volumeInfo"])
        # db.session.add(new_loc)
        # db.session.commit()
        return jsonify(
            201, f"Instances loaded: ") # {dig_data}", dict_data)

    def delete(self, _id):
        # delete a single book
        pass

    def put(self, _id):
        # update a single book
        pass
