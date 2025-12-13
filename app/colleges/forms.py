from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp


class CollegeForm(FlaskForm):
    id = HiddenField()
    code = StringField("College Code", 
                       validators=[DataRequired(), 
                                   Length(max=10)])
    name = StringField("College Name", 
                       validators=[DataRequired(), 
                                   Length(max=100)])
    submit = SubmitField("Save")

