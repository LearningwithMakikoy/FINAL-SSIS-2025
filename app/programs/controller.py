from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from . import program_bp
from .forms import ProgramForm
from .models import Program
from app.colleges.models import College



# PROGRAM ROUTES
@program_bp.route('', methods=['GET', 'POST'])
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
                    return redirect(url_for('program.programs'))
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
                return redirect(url_for('program.programs'))
            Program.create(code, name, college_code)

        flash("Program saved successfully.", "success")
        return redirect(url_for('program.programs'))
    
    #for the sorted searchby and paginated
    # GET REQUEST: Get filtered, sorted, and paginated programs
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    programs_list, total = Program.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )
    
        # Get ALL data (without pagination) for JavaScript
    all_programs, _ = Program.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=1,
        per_page=1000  
    )

    return render_template('programs.html',
                           form=form,
                           programs=programs_list,
                           colleges=colleges,
                           search=search,
                           sort_by=sort_by,
                           sort_dir=sort_dir,
                           page=page,
                           per_page=per_page,
                           total=total,
                           all_programs=all_programs)


@program_bp.route('/delete/<string:code>', methods=['POST'])
@login_required
def delete_program(code):
    prog = Program.get_by_code(code)
    if not prog:
        return jsonify(success=False, message="Program not found"), 404

    # ON DELETE SET NULL → safe to delete
    Program.delete(code)
    return jsonify(success=True, message="Program deleted")

#call the backend functions for search sort and pagination

@program_bp.route('/api')
@login_required
def api_programs():
    """API endpoint for AJAX requests to get filtered programs data"""
    # Read query parameters
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    # Fetch from model
    data, total = Program.get_filtered(
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

