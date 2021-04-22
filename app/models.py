from sqlalchemy import Column, Integer, Text, String
from app import db, mm


class Book(db.Model):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True,
                     nullable=True)
    book_id = Column(String)
    title = Column(Text, nullable=True)
    authors = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    thumbnail = Column(Text)
    categories = Column(String, nullable=True)
    average_rating = Column(Integer, nullable=True)
    ratings_count = Column(Integer, nullable=True)

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def __repr__(self):
        return f'{self.title}, {self.published_date}'


class BookSchema(mm.SQLAlchemyAutoSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Meta:
        model = Book
        sqla_session = db.session
        load_instance = True
        # fields = ['__all__']
        # exclude = ('categories', 'authors')
        # dump_only = ['thumbnail']
        # unknown = INCLUDE

    # thumbnail = fields.fields.Url()
    # categories = fields.fields.List(fields.fields.Str())
    # authors = fields.fields.List(fields.fields.Str())
