# src/web/app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from ..models import db
from ..brand_research.brand_research import research_brand

# Load environment variables
load_dotenv()
port = int(os.environ.get('PORT', 5000))

# Get the absolute path of the current file (app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the templates folder
templates_dir = os.path.join(current_dir, 'templates')

# Initialize the Flask app with the correct template folder
app = Flask(__name__, template_folder=templates_dir)

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hustler_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize extensions
db.init_app(app)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/hustler_ai.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Hustler AI startup')

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
@limiter.limit("5 per minute")
def do_research():
    app.logger.info("Research request received")
    brand_name = request.form['brand_name']
    user_company_info = request.form['user_company_info']
    outreach_goal = request.form['outreach_goal']
    desired_cta = request.form['desired_cta']
    app.logger.info(f"Researching brand: {brand_name}")
    try:
        results = research_brand(brand_name, user_company_info, outreach_goal, desired_cta)
        app.logger.info("Research completed successfully")
        return render_template('results.html', results=results, brand_name=brand_name)
    except Exception as e:
        app.logger.error(f"Error during research: {str(e)}")
        error_message = f"An error occurred during research: {str(e)}. Please try again."
        return render_template('error.html', error_message=error_message)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=port)
