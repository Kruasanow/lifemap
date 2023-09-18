from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, MultipleFileField, IntegerField, validators
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    short_description = TextAreaField('Краткое описание', validators=[DataRequired()])
    full_story = TextAreaField('Полная история')
    event_photo = FileField('Фото события')
    multiple_photos = MultipleFileField('Выберите до 20 фотографий', render_kw={"multiple": True})
    rating = IntegerField('Рейтинг', validators=[DataRequired(), validators.NumberRange(min=1, max=10)])

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replaced_string(stroka):
    try:
        left, right = stroka.split("\\")
    except Exception:
        left, right = '', ''
    return [left, right]
