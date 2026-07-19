from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.menu'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'Student')

        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for('auth.register'))

        try:
            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(full_name=full_name, email=email, password_hash=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created! Please login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard') if current_user.role == 'admin' else url_for('student.menu'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        # DEBUGGING PRINT (Check Railway logs for this)
        if not user:
            print(f"DEBUG: Login failed. No user found for email: {email}")
            flash("Invalid email or password.", "danger")
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.password_hash, password):
            print(f"DEBUG: Login failed. Password mismatch for user: {email}")
            flash("Invalid email or password.", "danger")
            return redirect(url_for('auth.login'))
        
        # If we reach here, user is valid
        print(f"DEBUG: Login successful for user: {email}")
        login_user(user, remember=True)
        
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.menu'))

    return render_template('login.html')