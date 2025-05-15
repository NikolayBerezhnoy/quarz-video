import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

class VideoLike(SqlAlchemyBase):
    __tablename__ = 'video_likes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    video_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('videos.id'))
    is_like = sqlalchemy.Column(sqlalchemy.Boolean)  # True for like, False for dislike
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)