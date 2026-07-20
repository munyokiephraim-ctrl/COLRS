from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.menu'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(email=email).first()
            
            login_allowed = False
            if user and user.password_hash:
                if user.password_hash.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
                    if check_password_hash(user.password_hash, password):
                        login_allowed = True
                else:
                    if user.password_hash == password:
                        user.password_hash = generate_password_hash(password)
                        db.session.commit()
                        login_allowed = True

            if login_allowed:

                print("====================================")
                print("LOGIN SUCCESS")
                print("Email:", user.email)
                print("Role :", user.role)
                print("====================================")

                login_user(user)

                flash("Logged in successfully!", "success")

                if user.role == "admin":
                    return redirect(url_for("admin.dashboard"))

                return redirect(url_for("student.menu"))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during login. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.menu'))

    if request.method == 'POST':
        try:
            full_name = request.form.get('full_name')
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password')
            
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email address already registered. Please log in.', 'warning')
                return redirect(url_for('auth.login'))
                
            hashed_password = generate_password_hash(password)
            new_user = User(
                full_name=full_name,
                email=email,
                password_hash=hashed_password,
                role='student',
                points_balance=0
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))