from app import create_app, db
from app.auth.routes import auth_bp
from app.student.routes import student_bp
from app.admin.routes import admin_bp
from flask import Flask

app = create_app()
app = Flask(__name__)

# Register them here
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(admin_bp, url_prefix='/admin')

# This is the magic block that forces table creation
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)