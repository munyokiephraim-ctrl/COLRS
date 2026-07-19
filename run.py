from app import create_app, db
from app.auth.routes import auth_bp
from app.student.routes import student_bp
from app.admin.routes import admin_bp

# 1. Initialize the app using your factory
# Do NOT create a new Flask instance after this
app = create_app()

# 2. Register blueprints to the app instance created by the factory
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')

# 3. Create database tables within the application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)