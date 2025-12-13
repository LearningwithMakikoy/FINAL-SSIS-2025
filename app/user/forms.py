from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField("Username", 
                           validators=[DataRequired(),
                                       Length(max=50)])
    password = PasswordField("Password", 
                             validators=[DataRequired()])
    submit = SubmitField("Login")

class SignupForm(FlaskForm):
    username = StringField("Username", 
                           validators=[DataRequired(), 
                                       Length(max=50)])
    email = StringField("Email", 
                        validators=[DataRequired(),
                                    Length(max=100)])
    password = PasswordField("Password", 
                             validators=[DataRequired()])
    submit = SubmitField("Sign Up")

