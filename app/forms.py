from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Optional, URL
from flask_pagedown.fields import PageDownField

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class GroupForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Сохранить')

class StudentForm(FlaskForm):
    name = StringField('Имя студента', validators=[DataRequired(), Length(max=128)])
    group_id = SelectField('Группа', coerce=int)
    submit = SubmitField('Сохранить')

class HomeworkForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = PageDownField('Задание', validators=[DataRequired()])
    publish_date = DateField('Дата публикации', validators=[DataRequired()])
    deadline = DateField('Дедлайн', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class HWSubmitForm(FlaskForm):
    github_url = StringField('Ссылка на Github', validators=[Optional(), URL()])
    submit = SubmitField('Отправить')
