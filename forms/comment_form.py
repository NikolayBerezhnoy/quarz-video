from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    comment = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')