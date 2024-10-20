# run.py
from src.web.app import app, create_tables

if __name__ == '__main__':
    create_tables()  # Call the function to create tables
    app.run(debug=True)