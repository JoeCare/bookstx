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


def queried_book():
    """Instead of get() one can use get_or_404()
    and instead of first() first_or_404().
    This will raise 404 errors instead of returning None:"""
    queried_book = Book.query.filter(Book.email.endswith('@example.com')).all()
    queried_book1 = Book.query.order_by(Book.title).all()
    queried_book2 = Book.query.limit(1).all()


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
    # elif filter_error is not None and sorting_error is not None:
    #     return jsonify(filter_error, sorting_error)
    # elif filter_error is None:
    #     return jsonify(sorting_error)
    # elif sorting_error is None:
    #     return jsonify(filter_error)
    # return jsonify(filter_error, sorting_error)

    # IF len(dict_of_queries) <= 2: xd

    # for k, v, in dict_of_queries.items():
    #     if k == "sort" and book_attrs_pattern.findall(v):
    #         if v.startswith("-"):
    #             order = 'DESC'
    #             column = v.replace("-", "")
    #         else:
    #             order = 'ASC'
    #             column = v
    #         sort_query = db.session.execute(
    #             f"SELECT * FROM books ORDER BY {column} {order};")
    #         # sort_query = db.session.execute(
    #         #     f"{final_query} ORDER BY {column} {order};")
    #         result = books_schema.dump(sort_query)
    #         print('res', result, 'q', sort_query)
    #         return jsonify(result)
    #     elif k == "sort":
    #         return jsonify({400: f'Error: Invalid parameter: {v}'},
    #                        use_of_queries)
    #     else:
    #         if k.endswith("_like"):
    #             column = k.replace("_like", "")
    #             value = v.replace("'", "").replace('"', '')
    #             filter_query = db.session.execute(
    #                 f"SELECT * FROM books WHERE {column} LIKE '%{value}%';")
    #             result = books_schema.dump(filter_query)
    #             print(result)
    #             if result:
    #                 return jsonify(result)
    #             else:
    #                 return jsonify({404: f'Error: Parameters not found: "'
    #                                      f'{value}"'},
    #                                use_of_queries)
    #         else:
    #             value = v.replace("'", "").replace('"', '')
    #             filter_query = db.session.execute(
    #                 f"SELECT * FROM books WHERE {k}='{value}';")
    #             result = books_schema.dump(filter_query)
    #             print(result)
    #             if result:
    #                 return jsonify(result)
    #             else:
    #                 return jsonify({404: f'Error: Parameters not found: "{v}"'},
    #                                use_of_queries)

    # db.session.add(result)
    # db.session.commit()
    # print('execute', result.fetchone())
    # print('execute', result.fetchall())
    # print('order_func_by:', dict_of_queries)
    # booksy = Book.query.filter_by(**dict_of_queries).all()
    # serialized = books_schema.dump(booksy)
    # print('serial', serialized)
    # books_p_asc = Book.query.order_by(
    #     Book.published_date.asc()).all()
    # published_asc = books_schema.dump(books_p_asc)
    #
    # books_p_desc = Book.query.order_by(
    #     Book.published_date.desc()).all()
    # published_desc = books_schema.dump(books_p_desc)
    #
    # books_t_asc = Book.query.order_by(
    #     Book.title.asc()).all()
    # title_asc = books_schema.dump(books_t_asc)
    #
    # books_t_desc = Book.query.order_by(
    #     Book.title.desc()).all()
    # title_desc = books_schema.dump(books_t_desc)

    order_by_fil_pattern = re.compile(r"\b" + r"\b|".join(
        ['order_by', 'filter']) + r"\b")
    auth_title_pattern = re.compile(r"\b" + r"\b|".join(
        ['authors', 'title']) + r"\b")
    cat_pub_pattern = re.compile(r"\b" + r"\b|".join(
        ['published_date', 'categories']) + r"\b")
    for k, v in dict_of_queries.items():
        sp = order_by_fil_pattern.findall(str(dict_of_queries))
        at = auth_title_pattern.findall(str(dict_of_queries))
        cp = cat_pub_pattern.findall(str(dict_of_queries))
        # print(k, v, dict_of_queries)

    # return title_asc, title_desc, published_asc, published_desc


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
                        print('to func', query_dict, 'w this', query_strings)
                custom_queried = ordered_books(query_strings)
                print('to func', query_dict, 'w this', query_strings)

                    # if "-" in query_dict["order_by"]:
                        #     ta, td, pa, pd = order_byed_books(query_dict)
                return custom_queried
                    #     return jsonify(td)
                    # elif query_dict["order_by"]:
                    #     ta, td, pa, pd = order_byed_books(query_dict)
                    #     return jsonify(ta)

                    # return jsonify({"?": query_string},
                    #                {400: 'Missing or invalid parameters!'})
                # return jsonify({400: 'Parameters required!'}, use_of_queries)
            else:
                print('List w/no queries')
                # return list without custom queries
                # resources = self.__db__.session.query(self.__model__).all()
                books = Book.query.all()
                print(books[:3])
                if books:
                    results = books_schema.dump(books)
                    return jsonify(results)
                else:
                    return jsonify({204: 'Storage is empty'})
        else:
            # resource = db.session.query(Book).get(_id)
            # if resource:
            #     print(resource)
            #     result = book_schema.dump(resource)
            #     return jsonify(result)
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
        :param:             table of which record will be created;
        :return:            201 on success, 406 if instance exists
        """
        data_set = request.get_json()
        to_obj = book_schema.load(data_set)
        print(to_obj)
        # new_book = Book(to_obj)
        db.session.add(to_obj)
        db.session.commit()
        return jsonify(
            201, f"Instance loaded: {to_obj}")  # {dig_data}", dict_data)

    # def delete(self, _id):
    #     """
    #     DELETE request response removes single record of
    #     given _id from database
    #     :param  _id:        unique identification number of record
    #
    #     """
    #     instance = self._resource(resource_id)
    #     self.__db__.session.delete(instance)
    #     self.__db__.session.commit()
    #     return jsonify({204: "Deleted"})
    #
    # def put(self, _id):
    #     # update a single book
    #     """Return response to HTTP PUT request."""
    #     instance = self._resource(resource_id)
    #     if instance is None:
    #         instance = self.__model__(   # pylint: disable=not-callable
    #             **request.get_json())
    #     else:
    #         instance.from_dict(request.get_json())
    #     resources = self.__db__.session.query(self.__model__).all()
    #     resource = self.__db__.session.query(self.__model__).get(resource_id)
    #     self.__db__.session.add(instance)
    #     self.__db__.session.commit()
    #     return self._created_response(instance.to_dict())
    #
    # def patch(self, _id):
    #     """Return response to HTTP PATCH request."""
    #     resource = self._resource(_id)
    #     resource.from_dict(request.get_json())
    #     self.__db__.session.add(resource)
    #     self.__db__.session.commit()
    #     return self._created_response(resource.to_dict())
