from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, IntegerField, SelectField,TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import User
from util.lang_list import lang_list, ocr_lang_list

class TranslatePDFForm(FlaskForm):
    upload = FileField('PDF to Translate', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF\'s Only!')
    ])
    from_lang = SelectField('From Language',
        choices = [("xx","Guess")]+lang_list
    )
    to_lang = SelectField('To Language',
        choices = [("en","English")]+lang_list
    )
    submit = SubmitField('Translate')

class TranslateFreeText(FlaskForm):
    body = TextAreaField('Text to Translate', validators=[
        DataRequired()
    ])
    to_lang = SelectField('To Language',
        choices = [("en","English")]+lang_list
    )
    submit = SubmitField('Translate')


class DictionaryAlternativesForm(FlaskForm):
    phrase = StringField('Text to Translate', validators=[
        DataRequired()
    ])
    from_lang = SelectField('From Language',
        choices = [("en","English")]+lang_list
    )
    to_lang = SelectField('To Language',
        choices = lang_list
    )
    submit = SubmitField('Translate')

class TranslateOCRForm(FlaskForm):
    upload = FileField('Picture to Translate', validators=[
        FileRequired(),
        FileAllowed(['jpg','jpeg','png'], 'JPEG, PNG Only!')
    ])
    from_lang = SelectField('From Language',
        choices = [("xx","Guess"), ('en','English')]+ocr_lang_list
    )
    to_lang = SelectField('To Language',
        choices = [("en","English")]+lang_list
    )
    mode = SelectField("Document Type",
        choices=[("Printed","Printed"), ("Handwritten","Handwritten")]
    )
    submit = SubmitField('Translate')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')