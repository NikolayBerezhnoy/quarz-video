from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired


class VideoUploadForm(FlaskForm):
    title = StringField('Название видео', validators=[DataRequired()])
    description = TextAreaField('Описание видео')
    video_file = FileField('Видеофайл (MP4)', validators=[DataRequired()])
    preview_file = FileField('Превью (PNG/JPG)', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
