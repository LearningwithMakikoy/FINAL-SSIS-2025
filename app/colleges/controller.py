from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from . import college_bp
from .forms import CollegeForm
from .models import College

# COLLEGE ROUTES

@college_bp.route('', methods=['GET', 'POST'])
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
                    return redirect(url_for('college.colleges'))
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
                return redirect(url_for('college.colleges'))
            College.create(code, name)

        flash("College saved successfully.", "success")
        return redirect(url_for('college.colleges'))

    # GET REQUEST: Get filtered, sorted, and paginated colleges
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    colleges_list, total = College.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )
    # Get ALL data (without pagination) for JavaScript
    all_colleges, _ = College.get_filtered(
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=1,
        per_page=10000  # Large number to get all matching records
    )
    
    return render_template('colleges.html',
                           form=form,
                           colleges=colleges_list,
                           search=search,
                           sort_by=sort_by,
                           sort_dir=sort_dir,
                           page=page,
                           per_page=per_page,
                           total=total,
                           all_colleges=all_colleges)


@college_bp.route('/delete/<string:code>', methods=['POST'])
@login_required
def delete_college(code):
    col = College.get_by_code(code)
    if not col:
        return jsonify(success=False, message="College not found"), 404

    # ON DELETE SET NULL → safe to delete
    College.delete(code)
    return jsonify(success=True, message="College deleted")

@college_bp.route('/api')
@login_required
def api_colleges():
    """API endpoint for AJAX requests to get filtered colleges data"""
    # Read query parameters
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_dir = request.args.get('sort_dir', 'asc', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    # Fetch from model
    data, total = College.get_filtered(
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


