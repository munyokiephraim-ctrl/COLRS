from app import create_app

# 1. Initialize the app using your factory
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)