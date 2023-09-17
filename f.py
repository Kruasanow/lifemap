from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, MultipleFileField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    short_description = TextAreaField('Краткое описание', validators=[DataRequired()])
    full_story = TextAreaField('Полная история')
    event_photo = FileField('Фото события')
    multiple_photos = MultipleFileField('Выберите до 20 фотографий', render_kw={"multiple": True})

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replaced_string(stroka):
    left, right = stroka.split("\\")
    return right