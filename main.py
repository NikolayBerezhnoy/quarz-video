import os
from flask import request, url_for, jsonify
from werkzeug.utils import secure_filename

import uuid
from flask_login import current_user
from forms.video_upload import VideoUploadForm
from flask import Flask, render_template, redirect, send_from_directory
from flask_login import LoginManager
from flask_login import login_user

from data import db_session
from data.users import User
from forms.comment_form import CommentForm
from forms.loginform import LoginForm
from forms.user import RegisterForm
from data.videos import Video
from data.likes import VideoLike

import sqlalchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "abc"
app.config['UPLOAD_FOLDER_VIDEOS'] = 'content/videos'
app.config['UPLOAD_FOLDER_PREVIEWS'] = 'content/previews'
app.config['ALLOWED_EXTENSIONS_VIDEO'] = {'mp4'}
app.config['ALLOWED_EXTENSIONS_PREVIEW'] = {'png', 'jpg', 'jpeg'}

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/quarz.db")
db_sess = db_session.create_session()

@app.route('/<path:path>')
def catch_all(path):
    return render_template('page404.html'), 404

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index(title='Домашняя страница', user_name='no-name'):
    db_sess = db_session.create_session()
    videos = db_sess.query(Video).options(sqlalchemy.orm.joinedload(Video.author_user))\
               .order_by(Video.modified_date.desc()).all()
    return render_template('all_videos.html', title=title, videos=videos)


@app.route('/previews/<filename>')
def get_preview(filename):
    return send_from_directory('content/previews', filename)


@app.route('/video/<int:id>')
def video(id):
    form = CommentForm()
    db_sess = db_session.create_session()

    # Получаем видео из базы данных
    video = db_sess.query(Video).filter(Video.id == id).first()

    if not video:
        return render_template('page404.html')

    # Получаем информацию об авторе
    author = db_sess.query(User).filter(User.id == video.author).first()

    # Проверяем существование видеофайла
    video_path = os.path.join('content', 'videos', f'{id}.mp4')
    video_exists = os.path.exists(video_path)

    # Увеличиваем счетчик просмотров
    video.views += 1
    db_sess.commit()

    user_liked = False  # Здесь должна быть проверка из базы данных
    user_disliked = False

    return render_template(
        'video.html',
        title=video.title,  # Используем реальный заголовок видео
        id=id,
        form=form,
        video_exists=video_exists,
        video=video,  # Передаем весь объект видео
        author=author,    # Передаем объект автора
        user_liked=user_liked,
        user_disliked=user_disliked
    )


# Маршрут для отдачи видеофайлов
@app.route('/content/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('content/videos', filename)


@app.route('/like_video/<int:video_id>', methods=['POST'])
def like_video(video_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Требуется авторизация'}), 401

    db_sess = db_session.create_session()

    # Проверяем существование видео
    video = db_sess.query(Video).get(video_id)
    if not video:
        return jsonify({'error': 'Видео не найдено'}), 404

    # Проверяем, ставил ли пользователь уже реакцию
    existing_reaction = db_sess.query(VideoLike).filter(
        VideoLike.user_id == current_user.id,
        VideoLike.video_id == video_id
    ).first()

    if existing_reaction:
        if existing_reaction.is_like:
            # Удаляем лайк
            db_sess.delete(existing_reaction)
            video.likes -= 1
        else:
            # Меняем дизлайк на лайк
            existing_reaction.is_like = True
            video.dislikes -= 1
            video.likes += 1
    else:
        # Добавляем новый лайк
        new_like = VideoLike(
            user_id=current_user.id,
            video_id=video_id,
            is_like=True
        )
        db_sess.add(new_like)
        video.likes += 1

    db_sess.commit()
    return jsonify({
        'likes': video.likes,
        'dislikes': video.dislikes,
        'user_liked': True,
        'user_disliked': False
    })


@app.route('/dislike_video/<int:video_id>', methods=['POST'])
def dislike_video(video_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Требуется авторизация'}), 401

    db_sess = db_session.create_session()

    video = db_sess.query(Video).get(video_id)
    if not video:
        return jsonify({'error': 'Видео не найдено'}), 404

    existing_reaction = db_sess.query(VideoLike).filter(
        VideoLike.user_id == current_user.id,
        VideoLike.video_id == video_id
    ).first()

    if existing_reaction:
        if not existing_reaction.is_like:
            # Удаляем дизлайк
            db_sess.delete(existing_reaction)
            video.dislikes -= 1
        else:
            # Меняем лайк на дизлайк
            existing_reaction.is_like = False
            video.likes -= 1
            video.dislikes += 1
    else:
        # Добавляем новый дизлайк
        new_dislike = VideoLike(
            user_id=current_user.id,
            video_id=video_id,
            is_like=False
        )
        db_sess.add(new_dislike)
        video.dislikes += 1

    db_sess.commit()
    return jsonify({
        'likes': video.likes,
        'dislikes': video.dislikes,
        'user_liked': False,
        'user_disliked': True
    })


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('q', '').strip()
    db_sess = db_session.create_session()

    if search_query:
        # Ищем видео, где название или описание содержит поисковый запрос
        videos = db_sess.query(Video).filter(
            (Video.title.ilike(f'%{search_query}%')) |
            (Video.description.ilike(f'%{search_query}%'))
        ).order_by(Video.modified_date.desc()).all()
    else:
        videos = []

    return render_template('search_results.html',
                           title=f'Результаты поиска: {search_query}',
                           videos=videos,
                           search_query=search_query)

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


@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = VideoUploadForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # Создаем запись о видео в базе данных
        video = Video(
            title=form.title.data,
            description=form.description.data,
            views=0,
            likes=0,
            dislikes=0,
            author=current_user.id
        )
        db_sess.add(video)
        db_sess.commit()

        # Получаем ID только что созданного видео
        video_id = video.id

        # Обработка видеофайла
        video_file = form.video_file.data
        if video_file and allowed_file(video_file.filename, app.config['ALLOWED_EXTENSIONS_VIDEO']):
            filename = secure_filename(f"{video_id}.mp4")
            video_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], filename)
            video_file.save(video_path)

        # Обработка превью
        preview_file = form.preview_file.data
        if preview_file and allowed_file(preview_file.filename, app.config['ALLOWED_EXTENSIONS_PREVIEW']):
            ext = preview_file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{video_id}.{ext}")
            preview_path = os.path.join(app.config['UPLOAD_FOLDER_PREVIEWS'], filename)
            preview_file.save(preview_path)

        return redirect(url_for('video', id=video_id))

    return render_template('upload_video.html', title='Загрузка видео', form=form)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def main():
    app.run()


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
