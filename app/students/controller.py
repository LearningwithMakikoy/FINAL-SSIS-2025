from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from . import student_bp
from .forms import  StudentForm 
from .models import Student 
from app.programs.models import Program
from app.supabase_client import upload_student_photo, delete_student_photo, get_supabase_client
import os
import re
import traceback

# STUDENT ROUTES

@student_bp.route('', methods=['GET', 'POST'])
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
        remove_photo = form.remove_photo.data == '1'

        # Check for duplicate ID BEFORE uploading photo
        if form.id.data:  # Editing existing student
            old_student_id = form.id.data.strip()
            
            # Check if student ID already exists (if changed)
            if old_student_id != student_id:
                existing = Student.get_by_id(student_id)
                if existing:
                    flash(f"Student ID '{student_id}' already exists.", "danger")
                    return redirect(url_for('student.students'))
        else:  # Creating new student
            # Check if student ID already exists
            existing = Student.get_by_id(student_id)
            if existing:
                flash(f"Student ID '{student_id}' already exists.", "danger")
                return redirect(url_for('student.students'))

        # Handle photo upload if provided - ONLY AFTER checking for duplicates
        photo_url = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename:
                try:
                    # Get file extension
                    file_ext = os.path.splitext(photo_file.filename)[1].lstrip('.')
                    if file_ext.lower() not in ['jpg', 'jpeg', 'png']:
                        flash("Invalid file type. Please upload JPG, JPEG, or PNG ", "danger")
                        return redirect(url_for('student.students'))
                    
                    # Read file data
                    file_data = photo_file.read()
                    if len(file_data) > 5 * 1024 * 1024:  # 5MB limit
                        flash("File too large. Maximum size is 5MB.", "danger")
                        return redirect(url_for('student.students'))
                    
                    # Upload to Supabase
                    photo_url = upload_student_photo(file_data, student_id, file_ext)
                except Exception as e:
                    flash(f"Error uploading photo: {str(e)}", "danger")
                    return redirect(url_for('student.students'))

        if form.id.data:  # Editing existing student
            old_student_id = form.id.data.strip()
            
            # Get existing student to preserve photo_url if not updating
            existing_student = Student.get_by_id(old_student_id)

            if remove_photo:
                if existing_student and existing_student.get('photo_url'):
                    try:
                        delete_student_photo(existing_student['photo_url'])
                    except Exception as e: 
                        print(f"Error in deleting photo: {str(e)}")
                photo_url = None # set to none to remove photo

            elif not photo_url and existing_student:
                #Keep existing photo if not uploaded new one and not removing
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
        return redirect(url_for('student.students'))
        
        # Get filter parameters from request
    filter_program = request.args.get('program', '')
    filter_year = request.args.get('year', '')
    filter_gender = request.args.get('gender', '')
    search_query = request.args.get('search', '')
   
    # Get all students with filtering
    students_list = Student.all_filtered(
        program=filter_program if filter_program else None,
        year=filter_year if filter_year else None,
        gender=filter_gender if filter_gender else None,
        search=search_query if search_query else None
        )    

    #search, sorted, and paginated students
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int) 

    # filter
    students_list, total = Student.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )
    all_students, _ = Student.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=1,
        per_page=10000 
    )
    
    return render_template('students.html',
                           form=form,
                           students=students_list,
                           programs=programs,
                           search=search,
                           sort_by=sort_by,
                           sort_dir=sort_dir,
                           page=page,
                           per_page=per_page,
                           total=total,
                           all_students=all_students)




@student_bp.route('/delete/<string:student_id>', methods=['POST'])
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


@student_bp.route('/upload-photo/<string:student_id>', methods=['POST'])
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
        if file_ext.lower() not in ['jpg', 'jpeg', 'png']:
            return jsonify(success=False, message="Invalid file type. Please upload JPG, JPEG, or PNG"), 400
        
        # Read file data
        file_data = photo_file.read()
        if len(file_data) > 5 * 1024 * 1024:  # 5MB limit
            return jsonify(success=False, message="File too large. Maximum size is 5MB."), 400
        
        # Get existing student to delete old photo
        existing_student = Student.get_by_id(student_id)

        # Delete existing photo(s) if they exist
        if existing_student:
            try:
                if existing_student.get(photo_url):
                    delete_student_photo(existing_student['photo_url'])
                supabase = get_supabase_client()
                bucket = supabase.storage.from_('SSIS')
                
                try:
                    bucket.remove(f"students/{student_id}.jpg")
                except: 
                    pass
            except Exception as e:
                print(f"Error deleting old photo:  {str(e)}" )

        
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


@student_bp.route('/api')
@login_required
def api_students():
    # Read query parameters
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    # Fetch from model
    data, total = Student.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "data": data,
        "total": total,
        "page": page,
        "per_page": per_page
    })