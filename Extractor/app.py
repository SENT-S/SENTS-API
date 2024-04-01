from dotenv import load_dotenv
import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from routes import v1_Blueprint

# Load the .env file
load_dotenv()

# Get the environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG', False)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS').split(',')

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

db.init_app(app)

# Initialize the migration engine
migrate = Migrate(app, db)

# Register the blueprints
app.register_blueprint(v1_Blueprint)

print(f'Running in {os.getenv("APP_ENV")} mode')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database table
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
