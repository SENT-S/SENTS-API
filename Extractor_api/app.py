from dotenv import load_dotenv
import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from routes import v1_Blueprint

# Load the .env file
load_dotenv()

# Get the APP_ENV value from the .env file
app_env = os.getenv("APP_ENV")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the correct configuration based on the APP_ENV environment variable
app.config.from_object(f'config.{app_env}')

db.init_app(app)

# Initialize the migration engine
migrate = Migrate(app, db)

# Register the blueprints
app.register_blueprint(v1_Blueprint)

print(f'Running in {os.getenv("APP_ENV")} mode')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database table
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=5000)
