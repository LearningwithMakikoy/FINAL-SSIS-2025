from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import bp
from .forms import  StudentForm, ProgramForm, CollegeForm, SignupForm, LoginForm
from app.models import Student, Program, College, User
from app.supabase_client import upload_student_photo, delete_student_photo
import os



# DASHBOARD / HOME

@bp.route('/')
@login_required
def index():
    return render_template('index.html')



# AUTH ROUTES


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
            flash("Username already taken", "danger")
            return redirect(url_for('user.signup'))
        
        #Check if email exist
        existing_email = User.get_by_email(email)
        if existing_email:
            flash("Email address already registered", "danger")
            return redirect(url_for('user.signup'))

        # Create user
        hashed_pw = generate_password_hash(password)
        new_user = User.create(username, email, hashed_pw)

        flash("Account created! You may now log in.", "success")
        return redirect(url_for('user.login'))

    return render_template('signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.get_by_username(username)

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for('user.login'))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for('user.index'))

    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('user.login'))



# PROGRAM ROUTES


@bp.route('/programs', methods=['GET', 'POST'])
@login_required
def programs():
    form = ProgramForm()

    # Prepare college choices: [(code, "code - name")]
    colleges = College.all()
    form.college_id.choices = [
        (c["code"], f"{c['code']} - {c['name']}") for c in colleges
    ]

    if form.validate_on_submit():
        code = form.code.data.strip()
        name = form.name.data.strip()
        college_code = form.college_id.data or None

        if form.id.data:  # Editing an existing program
            old_code = form.id.data.strip()
            # If code changed, we need to update the code (primary key)
            if old_code != code:
                # Check if new code already exists
                existing = Program.get_by_code(code)
                if existing:
                    flash(f"Program code '{code}' already exists.", "danger")
                    return redirect(url_for('user.programs'))
                # Update with new code (delete old, create new)
                Program.update_code(old_code, code, name, college_code)
            else:
                # Just update name and college
                Program.update(code, name, college_code)
        else:  # Creating a new program
            # Check if code already exists
            existing = Program.get_by_code(code)
            if existing:
                flash(f"Program code '{code}' already exists.", "danger")
                return redirect(url_for('user.programs'))
            Program.create(code, name, college_code)

        flash("Program saved successfully.", "success")
        return redirect(url_for('user.programs'))

    programs_list = Program.all()
    return render_template('programs.html',
                           form=form,
                           programs=programs_list,
                           colleges=colleges)


@bp.route('/programs/delete/<string:code>', methods=['POST'])
@login_required
def delete_program(code):
    prog = Program.get_by_code(code)
    if not prog:
        return jsonify(success=False, message="Program not found"), 404

    # ON DELETE SET NULL → safe to delete
    Program.delete(code)
    return jsonify(success=True, message="Program deleted")



# COLLEGE ROUTES


@bp.route('/colleges', methods=['GET', 'POST'])
@login_required
def colleges():
    form = CollegeForm()

    if form.validate_on_submit():
        code = form.code.data.strip()
        name = form.name.data.strip()

        if form.id.data:  # Editing
            old_code = form.id.data.strip()
            # If code changed, we need to update the code (primary key)
            if old_code != code:
                # Check if new code already exists
                existing = College.get_by_code(code)
                if existing:
                    flash(f"College code '{code}' already exists.", "danger")
                    return redirect(url_for('user.colleges'))
                # Update with new code (delete old, create new)
                College.update_code(old_code, code, name)
            else:
                # Just update the name
                College.update(code, name)
        else:  # Creating
            # Check if code already exists
            existing = College.get_by_code(code)
            if existing:
                flash(f"College code '{code}' already exists.", "danger")
                return redirect(url_for('user.colleges'))
            College.create(code, name)

        flash("College saved successfully.", "success")
        return redirect(url_for('user.colleges'))

    colleges_list = College.all()
    return render_template('colleges.html',
                           form=form,
                           colleges=colleges_list)


@bp.route('/colleges/delete/<string:code>', methods=['POST'])
@login_required
def delete_college(code):
    col = College.get_by_code(code)
    if not col:
        return jsonify(success=False, message="College not found"), 404

    # ON DELETE SET NULL → safe to delete
    College.delete(code)
    return jsonify(success=True, message="College deleted")



# STUDENT ROUTES

@bp.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    form = StudentForm()

    # Programs for dropdown
    programs = Program.all()
    form.program_id.choices = [
        (p["code"], f"{p['code']} - {p['name']}") for p in programs
    ]

    if form.validate_on_submit():
        student_id = form.id_number.data.strip()
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        program_code = form.program_id.data or None

        # Handle photo upload if provided
        photo_url = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename:
                try:
                    # Get file extension
                    file_ext = os.path.splitext(photo_file.filename)[1].lstrip('.')
                    if file_ext.lower() not in ['jpg', 'jpeg', 'png', 'gif']:
                        flash("Invalid file type. Please upload JPG, PNG, or GIF.", "danger")
                        return redirect(url_for('user.students'))
                    
                    # Read file data
                    file_data = photo_file.read()
                    if len(file_data) > 5 * 1024 * 1024:  # 5MB limit
                        flash("File too large. Maximum size is 5MB.", "danger")
                        return redirect(url_for('user.students'))
                    
                    # Upload to Supabase
                    photo_url = upload_student_photo(file_data, student_id, file_ext)
                except Exception as e:
                    flash(f"Error uploading photo: {str(e)}", "danger")
                    return redirect(url_for('user.students'))

        if form.id.data:  # Editing existing student
            old_student_id = form.id.data.strip()
            
            # Check if student ID already exists (if changed)
            if old_student_id != student_id:
                existing = Student.get_by_id(student_id)
                if existing:
                    flash(f"Student ID '{student_id}' already exists.", "danger")
                    return redirect(url_for('user.students'))
            
            # Get existing student to preserve photo_url if not updating
            existing_student = Student.get_by_id(old_student_id)
            if not photo_url and existing_student:
                photo_url = existing_student.get('photo_url')
            
            Student.update(
                old_student_id,
                student_id,
                first_name,
                last_name,
                program_code,
                form.year.data,
                form.gender.data,
                photo_url
            )
        else:  # Creating new student
            # Check if student ID already exists
            existing = Student.get_by_id(student_id)
            if existing:
                flash(f"Student ID '{student_id}' already exists.", "danger")
                return redirect(url_for('user.students'))
            
            Student.create(
                student_id,
                first_name,
                last_name,
                program_code,
                form.year.data,
                form.gender.data,
                photo_url
            )

        flash("Student saved successfully.", "success")
        return redirect(url_for('user.students'))

    students_list = Student.all()
    # Transform student data to match frontend expectations
    students_list = [
        {
            'id': s['id'],
            'id_number': s['id'],
            'first_name': s['firstname'],
            'last_name': s['lastname'],
            'program': s['program_name'] or s['course'] or '',
            'course': s['course'],
            'year': s['year'],
            'gender': s['gender'],
            'photo_url': s.get('photo_url') or ''
        }
        for s in students_list
    ]
    return render_template('students.html',
                           form=form,
                           students=students_list,
                           programs=programs)


@bp.route('/students/delete/<string:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    st = Student.get_by_id(student_id)
    if not st:
        return jsonify(success=False, message="Student not found"), 404

    # Delete photo from Supabase if exists
    if st.get('photo_url'):
        try:
            delete_student_photo(st['photo_url'])
        except Exception as e:
            print(f"Error deleting photo: {str(e)}")

    Student.delete(student_id)
    return jsonify(success=True, message="Student deleted")


@bp.route('/students/upload-photo/<string:student_id>', methods=['POST'])
@login_required
def upload_student_photo_route(student_id):
    """API endpoint to upload student photo separately."""
    try:
        if 'photo' not in request.files:
            return jsonify(success=False, message="No file provided"), 400
        
        photo_file = request.files['photo']
        if not photo_file or not photo_file.filename:
            return jsonify(success=False, message="No file selected"), 400
        
        # Validate file type
        file_ext = os.path.splitext(photo_file.filename)[1].lstrip('.')
        if file_ext.lower() not in ['jpg', 'jpeg', 'png', 'gif']:
            return jsonify(success=False, message="Invalid file type. Please upload JPG, PNG, or GIF."), 400
        
        # Read file data
        file_data = photo_file.read()
        if len(file_data) > 5 * 1024 * 1024:  # 5MB limit
            return jsonify(success=False, message="File too large. Maximum size is 5MB."), 400
        
        # Get existing student to delete old photo
        existing_student = Student.get_by_id(student_id)
        if existing_student and existing_student.get('photo_url'):
            try:
                delete_student_photo(existing_student['photo_url'])
            except Exception as e:
                print(f"Error deleting old photo: {str(e)}")
        
        # Upload to Supabase
        photo_url = upload_student_photo(file_data, student_id, file_ext)
        
        # Update student record
        if existing_student:
            Student.update(
                student_id,
                existing_student['firstname'],
                existing_student['lastname'],
                existing_student.get('course'),
                existing_student['year'],
                existing_student['gender'],
                photo_url
            )
        
        return jsonify(success=True, message="Photo uploaded successfully", photo_url=photo_url)
    except Exception as e:
        return jsonify(success=False, message=f"Error uploading photo: {str(e)}"), 500
