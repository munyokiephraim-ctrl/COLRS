from app import create_app, db
from app.auth.routes import auth_bp
from app.student.routes import student_bp
from app.admin.routes import admin_bp

# 1. Initialize the app using your factory
app = create_app()

# 2. Register blueprints
# Note: If your create_app() factory function already registers these blueprints, 
# you should remove these lines to avoid the "already registered" error.
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')

# 3. Create database tables within the application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)