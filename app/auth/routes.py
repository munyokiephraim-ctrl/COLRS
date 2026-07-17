from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.menu'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'Student') # Defaults to Student

        # Quick validation checks
        if not full_name or not email or not password:
            return "Error: Missing required fields", 400
            
        if password != confirm_password:
            return "Error: Passwords do not match", 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Error: Email address already registered", 400

        # Create new user with a securely hashed password
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return f"Success! Account created for {full_name}. You can now <a href='/auth/login'>Login here</a>."

    # Inline fallback HTML form for testing before we build templates
    return '''
        <h2>COLRS - Create Account</h2>
        <form method="POST">
            Name: <input type="text" name="full_name" required><br><br>
            Email: <input type="email" name="email" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            Confirm Password: <input type="password" name="confirm_password" required><br><br>
            Role: 
            <select name="role">
                <option value="Student">Student</option>
                <option value="Admin">Admin</option>
            </select><br><br>
            <button type="submit">Register</button>
        </form>
    '''

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.menu'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password hash matches
        if not user or not check_password_hash(user.password_hash, password):
            return "Error: Invalid email or password", 401

        login_user(user)
        
        # Role-based access control routing
        if user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.menu'))

    return '''
        <h2>COLRS - Login</h2>
        <form method="POST">
            Email: <input type="email" name="email" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            <button type="submit">Login</button>
        </form>
    '''

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return "You have logged out safely. <a href='/auth/login'>Login again</a>"