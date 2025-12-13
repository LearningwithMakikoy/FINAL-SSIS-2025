from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp


class ProgramForm(FlaskForm):
    id = HiddenField()
    code = StringField("Program Code", 
                       validators=[DataRequired(), 
                                   Length(max=10)])
    name = StringField("Program Name", 
                       validators=[DataRequired(), 
                                   Length(max=100)])
    college_id = SelectField("College", 
                             coerce=str, 
                             validators=[DataRequired()])
    submit = SubmitField("Save")

