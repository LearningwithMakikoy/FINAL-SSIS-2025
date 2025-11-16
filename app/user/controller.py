
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import bp
from .forms import StudentForm, ProgramForm, CollegeForm,SignupForm, LoginForm
from app.models import Student, Program, College, User


# DASHBOARD / INDEX

@bp.route('/')
@login_required
def index():
    return render_template('index.html')


#Signup Route
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data

        # Check if username exists
        existing = User.get_by_username(username)
        if existing:
            flash("Username is already taken", "danger")
            return redirect(url_for('user.signup'))

        hashed = generate_password_hash(password)
        new_user = User.create(username, email, hashed)

        if not new_user:
            flash("Error creating user", "danger")
            return redirect(url_for('user.signup'))

        flash("Account created! You may now log in.", "success")
        return redirect(url_for('user.login'))

    return render_template('auth/signup.html', form=form)


#login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.get_by_username(username)

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password", "danger")
            return redirect(url_for('user.login'))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for('user.index'))

    return render_template('auth/login.html', form=form)


# PROGRAM ROUTES

@bp.route('/programs', methods=['GET', 'POST'])
@login_required
def programs():
    form = ProgramForm()

    # Colleges are referenced by CODE now (VARCHAR PK)
    colleges = College.all()
    form.college_id.choices = [(c['code'], f"{c['code']} - {c['name']}") for c in colleges]

    if form.validate_on_submit():
        program_code = form.code.data.strip()
        name = form.name.data.strip()
        college_code = form.college_id.data if form.college_id.data != "" else None

        if form.id.data:  # editing existing
            Program.update(
                program_code,
                name,
                college_code
            )
        else:  # creating new
            Program.create(
                program_code,
                name,
                college_code
            )

        flash("Program saved successfully", "success")
        return redirect(url_for('user.programs'))

    programs_list = Program.all()
    return render_template('layouts/programs.html', form=form, programs=programs_list, colleges=colleges)


@bp.route('/programs/delete/<string:code>', methods=['POST'])
@login_required
def delete_program(code):
    prog = Program.get_by_code(code)
    if not prog:
        return jsonify(success=False, message="Program not found"), 404

    if prog.get('students_count', 0) > 0:
        return jsonify(success=False, message="Cannot delete program with enrolled students"), 400

    Program.delete(code)
    return jsonify(success=True, message="Program deleted")


# -------------------------
# COLLEGE ROUTES
# -------------------------
@bp.route('/colleges', methods=['GET', 'POST'])
@login_required
def colleges():
    form = CollegeForm()

    if form.validate_on_submit():
        code = form.code.data.strip()
        name = form.name.data.strip()

        if form.id.data:  # editing
            College.update(code, name)
        else:  # creating
            College.create(code, name)

        flash("College saved successfully", "success")
        return redirect(url_for('user.colleges'))

    colleges_list = College.all()
    return render_template('layouts/colleges.html', form=form, colleges=colleges_list)


@bp.route('/colleges/delete/<string:code>', methods=['POST'])
@login_required
def delete_college(code):
    col = College.get_by_code(code)
    if not col:
        return jsonify(success=False, message="College not found"), 404

    if col.get('programs_count', 0) > 0:
        return jsonify(success=False, message="Cannot delete college with linked programs"), 400

    College.delete(code)
    return jsonify(success=True, message="College deleted")


# -------------------------
# STUDENT ROUTES
# -------------------------
@bp.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    form = StudentForm()

    # Programs now referenced by CODE, not numeric ID
    programs = Program.all()
    form.program_id.choices = [(p['code'], f"{p['code']} - {p['name']}") for p in programs]

    if form.validate_on_submit():
        student_id = form.id_number.data.strip()

        if form.id.data:  # edit existing
            Student.update(
                student_id,
                form.first_name.data.strip(),
                form.last_name.data.strip(),
                form.program_id.data or None,
                form.year.data,
                form.gender.data
            )
        else:  # create new
            Student.create(
                student_id,
                form.first_name.data.strip(),
                form.last_name.data.strip(),
                form.program_id.data or None,
                form.year.data,
                form.gender.data
            )

        flash("Student saved successfully", "success")
        return redirect(url_for('user.students'))

    students_list = Student.all()
    return render_template('layouts/students.html', form=form, students=students_list, programs=programs)


@bp.route('/students/delete/<string:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    st = Student.get_by_id(student_id)
    if not st:
        return jsonify(success=False, message="Student not found"), 404

    Student.delete(student_id)
    return jsonify(success=True, message="Student deleted")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('user.login'))
