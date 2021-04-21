from sqlalchemy import Column, Integer, Text, JSON, String
from werkzeug.security import generate_password_hash as gpass
from werkzeug.security import check_password_hash as chpass
from app import app
from flask_marshmallow import Marshmallow, fields
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy.fields import Nested
from marshmallow_sqlalchemy import field_for
db = SQLAlchemy(app)
mm = Marshmallow(app)


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
    average_rating = Column(Integer)
    ratings_count = Column(Integer)

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def serialize(self):
        """Serialize record fields for list view"""
        return {
            "id": self.id,
            "ip_address": self.ip,
            "ip_type": self.type,
            "continent_name": self.continent_name,
            "country": self.country_name,
            "region": self.region_name,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            }

    def short(self):
        """Serialize record output with most essential fields."""
        return {
            "id": self.id,
            "ip_address": self.ip,
            "county_code": self.country_code,
            "city": self.city,
            }

    def __repr__(self):
        return f'{self.title}, {self.published_date}'


class BookSchema(mm.SQLAlchemyAutoSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Meta:
        model = Book
        # alchemy_session = db.session
        sqla_session = db.session
        load_instance = True
        # fields = ['__all__']
        # exclude = ('categories', 'authors')
        dump_only = ('thumbnail')

    thumbnail = fields.fields.Url()
    # categories = fields.fields.List(fields.fields.Str())
    # authors = fields.fields.List(fields.fields.Str())
