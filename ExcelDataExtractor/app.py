from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql import func
import pandas as pd

# Load the .env file
load_dotenv()

# Get the environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG', False)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS').split(',')

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# Blue print for V1 API
v1_Blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

# Define the database models


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    financial_statements = db.relationship(
        'FinancialStatement', backref='company', lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UploadedFile(db.Model):
    __tablename__ = 'uploaded_file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'company.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())


class FinancialStatement(db.Model):
    __tablename__ = 'financial_statement'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey(
        'company.id'), nullable=False)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@v1_Blueprint.route('/companies', methods=['GET'])
def get_companies():
    try:
        # Retrieve all companies from the database
        companies = Company.query.all()

        # If there are no companies, return an appropriate message
        if not companies:
            return jsonify({'message': 'No companies found', 'success': False}), 404

        # Convert the companies into a list of dictionaries
        response_data = [company.to_dict() for company in companies]

        return jsonify({'message': 'Companies retrieved successfully', 'success': True, 'data': response_data}), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


@v1_Blueprint.route('/financials/<int:company_id>', methods=['GET'])
def get_financials(company_id):
    try:
        # Retrieve the company with the given id
        company = Company.query.get(company_id)

        # If the company does not exist, return an error message
        if company is None:
            return jsonify({'message': f'Company with id {company_id} not found', 'success': False}), 404

        # Retrieve the financial statements for the given company id
        financials = FinancialStatement.query.filter_by(
            company_id=company_id).all()

        # Convert the financial statements into a list of dictionaries
        response_data = [financial.to_dict() for financial in financials]

        return jsonify({'message': 'Financial statements retrieved successfully', 'success': True, 'data': response_data}), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


@v1_Blueprint.route('/extract', methods=['POST'])
def add_financials():
    try:
        file = request.files.get('file')
        company_name = request.form.get('company_name')
        country_name = request.form.get('country')

        if file and company_name and country_name:
            company_name = company_name.lower().strip()
            country_name = country_name.lower().strip()

            uploaded_file = UploadedFile.query.filter_by(
                filename=file.filename).first()
            if uploaded_file:
                return jsonify({'message': 'File has already been uploaded for another company', 'success': False}), 400

            company = Company.query.filter_by(name=company_name).first()
            if not company:
                company = Company(name=company_name, country=country_name)
                db.session.add(company)
                db.session.commit()

            uploaded_file = UploadedFile(
                filename=file.filename, company_id=company.id)
            db.session.add(uploaded_file)

            data = pd.read_excel(file, sheet_name='Snapshot')

            # Convert DataFrame to dictionary, skipping empty rows
            data_dict = data.dropna(how='all').to_dict('records')

            # clean the data so that it can be stored in the database well for easy access in front end
            for row in data_dict:
                for key in row:
                    if isinstance(row[key], float):
                        row[key] = str(row[key])
                    if pd.isnull(row[key]):
                        row[key] = None

            # Save all rows of data to the database as an array of objects in a single record
            record = FinancialStatement(
                company_id=company.id, data=data_dict)
            db.session.add(record)
            db.session.commit()

            return jsonify({'message': 'Financial statements added successfully', 'success': True}), 200
        else:
            return jsonify({'message': 'No file or company name provided', 'success': False}), 400
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


# Register the blueprints
app.register_blueprint(v1_Blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database table
    app.run(host='0.0.0.0', debug=DEBUG)
