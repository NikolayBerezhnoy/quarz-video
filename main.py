import os

from flask import Flask, render_template, redirect, send_from_directory
from flask_login import LoginManager
from flask_login import login_user

from data import db_session
from data.users import User
from forms.loginform import LoginForm
from forms.user import RegisterForm
from forms.comment_form import CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "abc"

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/quarz.db")
db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index(title='Домашняя страница', user_name='no-name'):
    return render_template('all_videos.html', title=title, videos=[1, 2, 3, 4, 1, 2, 3, 1, 2, 3])


@app.route('/video/<int:id>')
def video(id):
    form = CommentForm()

    # Проверяем существование видеофайла
    video_path = os.path.join('content', 'videos', f'{id}.mp4')
    video_exists = os.path.exists(video_path)

    return render_template(
        'video.html',
        title=f'Видео #{id}',
        id=id,
        form=form,
        video_exists=video_exists  # Передаем информацию о наличии видео в шаблон
    )


# Маршрут для отдачи видеофайлов
@app.route('/content/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('content/videos', filename)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global db_sess
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return index('Welcome', user.name)
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    app.run()


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
