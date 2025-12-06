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

class CollegeForm(FlaskForm):
    id = HiddenField()
    code = StringField("College Code", 
                       validators=[DataRequired(), 
                                   Length(max=10)])
    name = StringField("College Name", 
                       validators=[DataRequired(), 
                                   Length(max=100)])
    submit = SubmitField("Save")

class StudentForm(FlaskForm):
    id = HiddenField()
    id_number = StringField(
        "Student ID",
        validators=[
            DataRequired(),
            Length(min=9, max=9, message="Student ID must be exactly 9 characters (YYYY-NNNN)"),
            Regexp(r'^\d{4}-\d{4}$', message="Student ID must be in format YYYY-NNNN (e.g., 2023-1234)")
        ]
    )
    first_name = StringField("First Name", 
                             validators=[DataRequired()])
    last_name = StringField("Last Name", 
                            validators=[DataRequired()])
    program_id = SelectField("Program", 
                             coerce=str, 
                             validators=[DataRequired()])
    year = SelectField("Year Level", 
                       choices=[
                                (1, "1"), 
                                (2, "2"), 
                                (3, "3"), 
                                (4, "4")], 
                       coerce=int,
                       validators=[DataRequired()])
    gender = SelectField("Gender", 
                         choices=[
                                  ("Male"), 
                                  ("Female"), 
                                  ("Other")], 
                        validators=[DataRequired()])
    remove_photo = HiddenField ('Remove Photo', default = '0' )
    submit = SubmitField("Save")
