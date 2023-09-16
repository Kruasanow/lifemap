# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt
from init_db import get_db_connection

app = Flask(__name__)
app.secret_key = 'ebanaya pomoyka'  # Random secret key for sessions
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Папка для загрузки файлов

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        sname = request.form['sname']
        email = request.form['email']
        admin = request.form.get('admin', 0)
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()  # Использование функции для установки соединения
        cur = conn.cursor()

        # Проверяем, существует ли такой email или username
        cur.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email or username already exists. Please choose another.', 'danger')
            cur.close()
            conn.close()
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("INSERT INTO users (username, fname, sname, email, admin, passwd) VALUES (%s, %s, %s, %s, %s, %s)",
                    (username, fname, sname, email, admin, hashed_password))
        conn.commit()
        cur.close()
        conn.close()

        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()  # Использование функции для установки соединения
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT passwd FROM users WHERE username = %s", (username,))
            stored_password = cur.fetchone()
        except Exception:
            stored_password = ''
        finally:
            cur.close()
            conn.close()
        print(stored_password)
        if stored_password and bcrypt.check_password_hash(stored_password[0], password):
            session['loggedin'] = True
            session['username'] = username

            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))  # Перенаправление на главную страницу

        else:
            flash('Login failed! Check your username and password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/createdescription', methods=['GET', 'POST'])
@login_required
def createdescription():
    from f import EventForm, allowed_file
    form = EventForm()
    if form.validate_on_submit():
        title = form.title.data
        short_description = form.short_description.data

        # Выводим в консоль
        print(title, short_description)

        # Создаем основную директорию для события
        event_folder = os.path.join(app.config['UPLOAD_FOLDER'], title)
        if not os.path.exists(event_folder):
            os.makedirs(event_folder)

        # Сохраняем основное фото, если оно есть
        f = form.event_photo.data
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(event_folder, filename))

        # Сохраняем галерею фото, если они есть
        gallery_photos = request.files.getlist('multiple_photos')
        if gallery_photos:
            gallery_folder = os.path.join(event_folder, "галерея фото")
            if not os.path.exists(gallery_folder):
                os.makedirs(gallery_folder)

            for upload in gallery_photos:
                if upload and upload.filename and allowed_file(upload.filename):
                    filename = secure_filename(upload.filename)
                    upload.save(os.path.join(gallery_folder, filename))

        return redirect(url_for('createdescription'))

    return render_template('createdescription.html', form=form)

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
    flash('Button was pressed!')
    return redirect(url_for('createdescription'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
