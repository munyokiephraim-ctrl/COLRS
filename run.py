from app import create_app, db
from app.auth.routes import auth_bp
from app.student.routes import student_bp
from app.admin.routes import admin_bp

# 1. Initialize the app using your factory
app = create_app()


# 3. Create database tables within the application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)