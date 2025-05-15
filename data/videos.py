import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Video(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('users.id'))
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)

    # Удаляем email, так как он не нужен в модели видео
    # email = sqlalchemy.Column(sqlalchemy.String, unique=True)

    # Добавляем связь с пользователем
    author_user = orm.relationship('User', back_populates='videos')

    def __repr__(self):
        return f"Video(id={self.id}, title='{self.title}', author={self.author})"