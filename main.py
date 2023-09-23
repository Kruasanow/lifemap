# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt
from init_db import get_db_connection
from functools import wraps
from sensetive_data import admin_key, app_secret_key
from f import EventForm, allowed_file, replaced_string, check_admin, get_maps, replace_huetu

app = Flask(__name__)
app.secret_key = app_secret_key  # Random secret key for sessions
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Папка для загрузки файлов

ADMIN_KEY = admin_key

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/switch_user', methods=['POST'])
def switch_user():
    new_username = request.form.get('username')
    # В этом месте вы должны добавить код для проверки, разрешено ли текущему пользователю становиться другим пользователем
    session['username'] = new_username
    return redirect(url_for('main'))

@app.route('/switch_map_main', methods=['POST'])
def switch_map_index():
    map = request.form.get('map_main')
    # В этом месте вы должны добавить код для проверки, разрешено ли текущему пользователю становиться другим пользователем
    session['map_main'] = map
    return redirect(url_for('main'))

# @app.route('/switch_map', methods=['POST'])
# def switch_map():
#     map = request.form.get('map')
#     # В этом месте вы должны добавить код для проверки, разрешено ли текущему пользователю становиться другим пользователем
#     session['map'] = map
#     return redirect(url_for('index'))


@app.route('/delete_event/<int:event_id>')
@admin_required
@login_required
def delete_event(event_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = %s;", (event_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Событие успешно удалено!', 'success')
    return redirect(url_for('cabinet'))


# @app.before_request
# def restore_original_username():
#     # Проверяем, является ли конечная точка не 'main' и есть ли в сессии 'original_username'
#     if request.endpoint != 'main' and 'original_username' in session:
#         session['username'] = session['original_username']

# @app.before_request
# def set_original_username():
#     if 'username' in session and 'original_username' not in session:
#         session['original_username'] = session['username']

# @app.after_request
# def restore_original_username(response):
#     if 'original_username' in session:
#         session['username'] = session['original_username']
#     return response

@app.before_request
def handle_username():
    # Устанавливаем original_username, если он еще не установлен.
    if 'username' in session and 'original_username' not in session:
        session['original_username'] = session['username']
    
    # Если текущий запрос не к странице /main, восстанавливаем оригинальное имя пользователя.
    if request.endpoint != 'main' and 'original_username' in session:
        session['username'] = session['original_username']


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        sname = request.form['sname']
        email = request.form['email']
        admin = request.form.get('admin', 0)
        username = request.form['username']
        password = request.form['password']
        secret = request.form['secret']

        conn = get_db_connection()  # Использование функции для установки соединения
        cur = conn.cursor()

        # Проверяем, существует ли такой email или username
        cur.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()

        if existing_user:
            flash('E-mail и/или никнейм уже существуют. Ты не оригинален.', 'danger')
            cur.close()
            conn.close()
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("INSERT INTO users (username, fname, sname, email, admin, passwd, secret) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (username, fname, sname, email, admin, hashed_password, secret))
        conn.commit()
        cur.close()
        conn.close()

        flash('Успешная регистрация! Выполните вход.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        username = session['username']
    except Exception:
        username = 'Вы еще не вошли в аккаунт'
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        maps = get_maps()
    except Exception:
        print('hueta s maps')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_key = request.form.get('admin_key', '')
        current_map = request.form['map']

        cur.execute("SELECT filename FROM maps WHERE city_name = %s", (current_map,))
        current_map_file = cur.fetchone()
        session['current_map'] = current_map_file

        try:
            cur.execute("SELECT passwd FROM users WHERE username = %s", (username,))
            stored_password = cur.fetchone()
        except Exception:
            stored_password = ''
        finally:
            cur.close()
            conn.close()

        if stored_password and bcrypt.check_password_hash(stored_password[0], password):
            session['loggedin'] = True
            session['original_username'] = username
            session['username'] = username

            # Проверка на наличие прав админа
            if admin_key == ADMIN_KEY:
                session['is_admin'] = True
                flash('Успешный вход в режиме суперпользователя', 'success')
                return redirect(url_for('main'))
            else:
                session['is_admin'] = False
                flash('Успешный вход в режиме пользователя!', 'success')
                return redirect(url_for('index'))

        else:
            flash('Ошибка входа! Проверьте никнейм и/или пароль.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', username = username, admin_mode = check_admin(), maps = maps)


@app.route('/addfriend', methods=['GET', 'POST'])
@admin_required
@login_required
def addfriend():
    if request.method == 'POST':
        friend_name = request.form['username']
        check_email = request.form['password']
        admin_key = request.form['admin_key']
        current_session_user = session['username']

        conn = get_db_connection()  # Использование функции для установки соединения
        cur = conn.cursor()
        try:
            cur.execute('SELECT email, secret FROM users WHERE username = %s;', (friend_name,))
            result = cur.fetchall()

            # Если результат не пустой
            if result:
                email, secret = result[0]

                # Проверка на существование друга в user_friends
                cur.execute('SELECT private FROM user_friends WHERE username = %s AND friend = %s;', (current_session_user, friend_name))
                friend_existence = cur.fetchone()

                if email == check_email:
                    if secret == admin_key:
                        private_value = True
                        message = 'Added friend with full access!'

                        # Если друг уже существует и private был False, обновляем его значение
                        if friend_existence and not friend_existence[0]:
                            cur.execute('UPDATE user_friends SET private = %s WHERE username = %s AND friend = %s;', (True, current_session_user, friend_name))
                        # Иначе добавляем друга в список
                        elif not friend_existence:
                            cur.execute("INSERT INTO user_friends (username, friend, private) VALUES (%s, %s, %s)", (current_session_user, friend_name, private_value))

                    else:
                        private_value = False
                        message = 'Added friend with restricted access!'

                        # Если друг не существует, добавляем его в список
                        if not friend_existence:
                            cur.execute("INSERT INTO user_friends (username, friend, private) VALUES (%s, %s, %s)", (current_session_user, friend_name, private_value))

                conn.commit()

                flash(message, 'success')
                
            else:
                flash('No such user found!', 'error')

        except Exception as e:
            print('Error:', e)
            flash('Something went wrong!', 'error')
        cur.close()
        conn.close()

        return redirect(url_for('addfriend'))

    return render_template('addfriend.html', admin_mode = check_admin(), username = session['username'])

@app.route('/main', methods=['GET', 'POST'])
@login_required
@admin_required
def main():

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        session['username'] = request.form['username']

    original_username = session.get('original_username', 'Вы еще не вошли в аккаунт')

    # Выбираем всех друзей
    cur.execute("SELECT friend, private FROM user_friends WHERE username = %s;", (original_username,))
    friends_data = cur.fetchall()
    friends = [friend[0] for friend in friends_data]
    close_friends = [friend[0] for friend in friends_data if friend[1]]

    cur.execute("SELECT username FROM users")
    users = [user[0] for user in cur.fetchall()]

    # Если выбранный пользователь - это близкий друг
    if session['username'] in close_friends:
        cur.execute('SELECT * FROM events WHERE owner_name = %s AND map = %s;', 
                    (session['username'], session['current_map']))
    # Если выбранный пользователь - это просто друг
    elif session['username'] in friends:
        cur.execute('SELECT * FROM events WHERE owner_name = %s AND map = %s AND is_private = 0;', 
                    (session['username'], session['current_map']))
    else:
        cur.execute('SELECT * FROM events WHERE owner_name = %s AND map = %s;', (original_username, session['current_map']))

    data = cur.fetchall()
    cmap = replace_huetu(session['current_map'])
    extracted = [[t[1], t[2], t[3], replaced_string(t[5])] for t in data]

    cur.close()
    conn.close()

    return render_template('main.html', ext=extracted, users=users, cmap=cmap, username=original_username, admin_banner=check_admin())


@app.route('/cabinet')
@login_required
def cabinet():
    username = session['username']

    conn = get_db_connection()
    cur = conn.cursor()

    # Количество друзей
    cur.execute("SELECT COUNT(*) FROM user_friends WHERE username = %s;", (username,))
    total_friends = cur.fetchone()[0]

    cur.execute("SELECT friend, private FROM user_friends WHERE username = %s;", (username,))
    friends_data = cur.fetchall()

    # Количество близких друзей
    cur.execute("SELECT COUNT(*) FROM user_friends WHERE username = %s AND private = TRUE;", (username,))
    close_friends = cur.fetchone()[0]

    # Информация о пользователе
    cur.execute("SELECT fname, sname, email, date_added FROM users WHERE username = %s;", (username,))
    user_data = cur.fetchone()
    full_name = f"{user_data[0]} {user_data[1]}"
    email = user_data[2]
    date_registered = user_data[3]

    # Количество событий пользователя
    cur.execute("SELECT COUNT(*) FROM events WHERE owner_name = %s;", (username,))
    total_events = cur.fetchone()[0]

    # Количество фотографий
    cur.execute("SELECT SUM(ARRAY_LENGTH(gallery_photos, 1)) FROM events WHERE owner_name = %s;", (username,))
    total_photos = cur.fetchone()[0] or 0  # Если возвращает None

    # Средний рейтинг
    cur.execute("SELECT AVG(rating) FROM events WHERE owner_name = %s;", (username,))
    avg_rating_raw = cur.fetchone()[0]
    avg_rating = round(avg_rating_raw, 2) if avg_rating_raw is not None else 0

    # Статистика рейтинга
    ratings_stats = {}
    for i in range(1, 11):  # Если у вас рейтинг от 1 до 5
        cur.execute("SELECT COUNT(*) FROM events WHERE owner_name = %s AND rating = %s;", (username, i))
        ratings_stats[i] = cur.fetchone()[0]

    # Приватные события
    cur.execute("SELECT COUNT(*) FROM events WHERE owner_name = %s AND is_private = 1;", (username,))
    private_events_count = cur.fetchone()[0]

    cur.execute("SELECT id, title, photo, short_description FROM events WHERE owner_name = %s;", (username,))
    events = cur.fetchall()


    cur.close()
    conn.close()

    return render_template('cabinet.html',
                           admin_mode = check_admin(),
                           events = events,
                           friends=friends_data,
                           username=username, 
                           total_friends=total_friends, 
                           close_friends=close_friends, 
                           full_name=full_name, 
                           email=email, 
                           date_registered=date_registered, 
                           total_events=total_events, 
                           total_photos=total_photos, 
                           avg_rating=avg_rating, 
                           ratings_stats=ratings_stats,
                           private_events_count=private_events_count)

@app.route('/article/<path:unique_identifier>')
def article(unique_identifier):
    try:
        username = session['username']
    except Exception:
        username = 'Вы еще не вошли в аккаунт'
    # Разбить unique_identifier на две части: имя пользователя и название события
    username, event_title = unique_identifier.split("_", 1)
    print(unique_identifier)

    cur = get_db_connection().cursor()
    cur.execute('SELECT * FROM events WHERE owner_name = %s AND title = %s;', (username, event_title))
    event = cur.fetchone()
    if not event:
        return "Статья не найдена", 404
    return render_template('article.html', event=event, username = username, admin_mode = check_admin())

@app.route('/')
@login_required
def index():

    try:
        maps = get_maps()
    except Exception:
        print('hueta s maps')
    
    try:
        username = session['username']
    except Exception:
        username = 'Вы еще не вошли в аккаунт'
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM events WHERE owner_name = %s AND map = %s;', (session['username'], session['current_map']))

    data = cur.fetchall()
    # for t in data:
        # print(t)
    extracted = [[t[1], t[2], t[3], replaced_string(t[5])] for t in data]
    cmap = replace_huetu(session['current_map'])
    print(cmap)
    # print(extracted)
    return render_template('index.html', ext = extracted, username = username, admin_mode = check_admin(), cmap = cmap)

@app.route('/createdescription', methods=['GET', 'POST'])
@login_required
def createdescription():
    try:
        username = session['username']
    except Exception:
        username = 'Вы еще не вошли в аккаунт'

    cmap = replace_huetu(session['current_map'])

    form = EventForm()
    if form.validate_on_submit():
        title = form.title.data
        short_description = form.short_description.data
        full_description = form.full_story.data
        rating = form.rating.data
        is_private = 1 if form.is_private.data else 0

        # Создаем основную директорию для события
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        event_folder = os.path.join(user_folder, title)

        if not os.path.exists(event_folder):
            os.makedirs(event_folder)

        # Сохраняем основное фото, если оно есть
        f = form.event_photo.data
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(event_folder, filename))
            photo_path = os.path.join(title, filename)  # Путь к сохраненному фото

        else:
            photo_path = None

        # Сохраняем галерею фото, если они есть
        gallery_photos = request.files.getlist('multiple_photos')
        gallery_paths = []
        if gallery_photos:
            gallery_folder = os.path.join(event_folder, "галерея фото")
            if not os.path.exists(gallery_folder):
                os.makedirs(gallery_folder)

            for upload in gallery_photos:
                if upload and upload.filename and allowed_file(upload.filename):
                    filename = secure_filename(upload.filename)
                    upload.save(os.path.join(gallery_folder, filename))
                    gallery_paths.append(os.path.join(title, "галерея фото", filename))  # Пути к сохраненным фото

        else:
            gallery_paths = []

        try:
            coords = session['X'] + ':' + session['Y']
            
            # Удалите координаты из сессии сразу после их использования
            session.pop('X', None)
            session.pop('Y', None)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute('INSERT INTO events (coords, title, short_description, full_description, photo, gallery_photos, rating, owner_name, is_private, map) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (coords, title, short_description, full_description, photo_path, gallery_paths, rating, session['username'], is_private, cmap))


            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            flash('Выберите координаты')
            print("kakaya-to hueta" + str(is_private))
        # Вставляем данные в базу данных


        return redirect(url_for('createdescription'))

    return render_template('createdescription.html', form=form, username = username, cmap = cmap)

@app.route('/save_coordinates', methods=['POST'])
def save_coordinates():
    x = request.form.get('x')
    y = request.form.get('y')
    
    # Здесь вы можете обработать или сохранить координаты, как вам нужно
    print(f"X: {x}, Y: {y}")
    session['X'] = x
    session['Y'] = y
    return jsonify(status="success")

@app.route('/button_pressed', methods=['POST'])
def button_pressed():
    # Здесь выполняется обработка нажатия кнопки
    # flash('Button was pressed!')
    return redirect(url_for('createdescription'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
