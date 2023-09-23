from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, MultipleFileField, IntegerField, validators, BooleanField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    short_description = TextAreaField('Краткое описание', validators=[DataRequired()])
    full_story = TextAreaField('Полная история')
    event_photo = FileField('Фото события')
    multiple_photos = MultipleFileField('Выберите до 20 фотографий', render_kw={"multiple": True})
    rating = IntegerField('Рейтинг', validators=[DataRequired(), validators.NumberRange(min=1, max=10)])
    is_private = BooleanField('Сделать событие приватным')  

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replaced_string(stroka):
    try:
        left, right = stroka.split("\\")
    except Exception:
        left, right = '', ''
    return [left, right]


            # <label for="admin_key" id="admin_key_label" style="display: none;">Ключ:
            #     <input type="password" id="admin_key" name="admin_key" style="display: none;">
            # </label>

def check_admin():
    from flask import session
    try:
        if session['is_admin'] == True:
            admin_banner = '[Суперпользователь]'
        else:
            admin_banner = '[Пользователь]'
    except Exception:
        session['is_admin'] = '[Роль не выбрана]'
        admin_banner = session['is_admin']
    return admin_banner


def get_maps():
    from init_db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT city_name, filename FROM maps;')
    maps = cur.fetchall()
    
    cur.close()
    conn.close()
    
    #[
    # ('Краснодар', '/static/img/maps/krasnodar.png'), 
    # ('Санкт-Петербург', '/static/img/maps/spb.png'), 
    # ('Белая-Глина', '/static/img/maps/belaya.png')
    # ]
    return maps

def replace_huetu(stroka):
    stroka = str(stroka).replace('(','').replace(')','').replace(',','').replace("'",'')
    return stroka