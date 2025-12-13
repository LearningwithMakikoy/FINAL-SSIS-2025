from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp


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
