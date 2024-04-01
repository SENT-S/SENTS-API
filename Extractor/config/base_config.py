from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

DEBUG = os.getenv('DEBUG', False)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS').split(',')
