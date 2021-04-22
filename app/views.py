import json

from flask.views import MethodView, View
from .models import Book, BookSchema, db, mm
from flask import request, jsonify
import requests, re


book_schema = BookSchema()
books_schema = BookSchema(many=True)
use_of_queries = [
                "API response customization. Query through URL.",
                "Type one of the valid variables after "
                "quotation mark",
                {
                    "Basic usage": "/resource?query",
                    "Attribute NOTICE": "Misspelled attributes are ignored!",
                    "Attributes": "authors, authors_like, published_date, "
                                  "categories, categories_like "
                                  "title, title_like",
                    "Examples": [
                        {
                            "/resource?published_date=1882":
                                "This return only records published at "
                                "given date"
                            },
                        {
                            "/resource?authors='Jan Morsztyn'":
                                "Return only records written by specified "
                                "authors"
                            },
                        {
                            "/resource?authors_like=Jan":
                                "Return all records written by authors "
                                "with similar names"
                            },
                        {
                            "/resource?categories=Algorithms":
                                "Return only records of that particular "
                                "category/categories"
                            },
                        {
                            "/resource?categories_like=Rel":
                                "Return all records containing given phrase "
                                "within it's categories labels"
                            },
                        {
                            "/resource?title='The Hobbit,"
                            " Or There and Back Again'":
                                "Return only records of given title"
                            },
                        {
                            "/resource?title_like='Hobbit'":
                                "Return all records with title similar to or "
                                "containing given phrase"
                            },
                        {
                            "/resource?sort=-authors":
                                "Return list of records sorted according to "
                                "authors names in descending order"
                            },
                        {
                            "/resource?sort=published_date":
                                "Return list of records sorted according to"
                                " publication time in ascending order"
                            },
                        ],
                    },
                ]


def ordered_books(dict_of_queries):
    """
    Return serialized book objects with ordering depending on
    parameters passed to function.
    """
    book_attrs = ['authors', 'published_date', 'categories', 'title']
    book_attrs_pattern = re.compile(r"\b" + r"\b|".join(book_attrs) + r"\b",
                                    re.IGNORECASE)
    order = None
    by_column = None
    base_query = f"SELECT * FROM books"
    filter_query = None
    sort_query = None
    filter_error = None
    sorting_error = None
    filter_like_error = None
    for k, v, in dict_of_queries.items():
        if k == "sort" and book_attrs_pattern.findall(v):
            if v.startswith("-"):
                order = 'DESC'
                by_column = v.replace("-", "")
            else:
                order = 'ASC'
                by_column = v
            sort_query = f"ORDER BY {by_column} {order}"
            # sort_query = db.session.execute(
            #     f"{base_query} ORDER BY {by_column} {order};")
        elif k == "sort":
            sorting_error = {400: f'Sorting error: Invalid parameter: "{v}"'}
        else:
            if k.endswith("_like"):
                column = k.replace("_like", "")
                value = v.replace("'", "").replace('"', '')
                filter_query = f"WHERE {column} LIKE '%{value}%'"
                check_filter = db.session.execute(f"{base_query} {filter_query}")
                if books_schema.dump(check_filter):
                    pass
                else:
                    filter_error = {404: f'Filter error: Parameters not found: '
                                         f'"{v}"'}
            else:
                value = v.replace("'", "").replace('"', '')
                filter_query = f"WHERE {k}='{value}'"
                check_filter = db.session.execute(f"{base_query} {filter_query}")
                if books_schema.dump(check_filter):
                    pass
                else:
                    filter_error = {404: f'Filter error: Parameters not found: '
                                         f'"{v}"'}
    # q_dict = {}
    errors = []
    custom_query = f"{filter_query} {sort_query}".replace("None","")
    print(custom_query)
    final_query = f"{base_query} {custom_query}"
    print(final_query)
    # result = books_schema.dump(db.session.execute(final_query))
    if filter_error or sorting_error:
        if filter_error:
            errors.append(filter_error)
        if sorting_error:
            errors.append(sorting_error)
        # if filter_like_error:
        #     errors.append(filter_like_error)
        return jsonify(errors, use_of_queries)
    if filter_query or sort_query:
        result = books_schema.dump(db.session.execute(final_query))
        return jsonify(result)


class BookScrap(MethodView):

    def post(self):
        body = request.get_json()
        books_url = f"https://www.googleapis.com/books/v1/volumes?q={body['q']}"
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
            # data_to_obj = book_schema.load(book_dict)
            # print(data_to_obj)
            new_book = Book(book_dict)
            db.session.add(new_book)
            # db.session.add(data_to_obj)
            db.session.commit()
        return jsonify(
            201, f"Instances loaded: {len(book_items)}")


# query_strings_mapper = {
#     "order_by": Book.query.order_by()
#
#     }
# same = set(query_string).intersection(set(queries))
# if re.compile('|'.join(queries), re.IGNORECASE).search(
#         str(query_string)):


class BooksCrudAPI(MethodView):

    def get(self, _id):
        """
        Return list of all records at /books or particular one at /books/<id>
        :param _id:                 main ID number of record in our database
        :return single record:      retrieved according to given _id
        :return collection:         return all records of /books resource
        """
        if _id is None:
            query_dict = {}
            query_dict["sort"] = request.args.get('sort')
            query_dict["authors"] = request.args.get('authors')
            query_dict["authors_like"] = request.args.get('authors_like')
            query_dict["published_date"] = request.args.get('published_date')
            query_dict["categories"] = request.args.get('categories')
            query_dict["categories_like"] = request.args.get('categories_like')
            query_dict["title"] = request.args.get('title')
            query_dict["title_like"] = request.args.get('title_like')
            if any(query_dict.values()): #  and any(query_dict.values()):
                print('querydict:', query_dict)
                query_strings = {}
                for k, v in query_dict.items():
                    if v:
                        query_strings[k] = v
                        print('Possible:', query_dict, 'not None:',
                              query_strings)
                custom_queried = ordered_books(query_strings)
                return custom_queried
            else:
                print('List without queries')
                books = Book.query.all()
                print(books[:3])
                if books:
                    results = books_schema.dump(books)
                    return jsonify(results)
                else:
                    return jsonify({204: 'Storage is empty'})
        else:
            book = Book.query.filter_by(id=_id).one_or_none()
            if book:
                print(book)
                result = book_schema.dump(book)
                return jsonify(result)
            else:
                return jsonify({404: 'Record not found'})

    def post(self):
        """
        Create a new  record from data object passed within request body
        :param body:        table of which record will be created;
        :return:            201 on success, 406 if instance exists
        """
        data_set = request.get_json()
        # to_obj = book_schema.load(request.get_json())
        # print(to_obj)
        new_book = Book(data_set)
        db.session.add(new_book)
        # db.session.add(to_obj)
        db.session.commit()
        return jsonify(201, f"Instance loaded: {new_book}")
        # return jsonify(201, f"Instance loaded: {to_obj}")

    def delete(self, _id):
        """
        DELETE request response removes single record of
        given _id from database
        :param  _id:        unique identification number of record
        :return:            204 if succeeded, or 404 error
        """
        book = Book.query.filter_by(id=_id).one_or_none()
        if book:
            db.session.delete(book)
            db.session.commit()
            return jsonify({204: "Deleted"})
        else:
            return jsonify({404: "Record ID not found"})

    def put(self, _id):
        """
        Update a record with data passed within request body
        :param _id:         unique ID of the record to update;
        :param body:        table with data to update record;
        :return:            200 on success, 404 if not found
        """
        book = Book.query.filter_by(id=_id).one_or_none()
        if book:
            new_book = book_schema.load(request.get_json())
            new_book.id = book.id
            db.session.merge(new_book)
            db.session.commit()
            response = (200, f'Record updated for ID: {_id}')
        else:
            response = (404, f'Record not found for ID: {_id}')
        return jsonify(response)
