from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql import func
import pandas as pd

# Load the .env file
load_dotenv()

# Get the environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG', False)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS')

# Convert ALLOWED_ORIGINS from a comma-separated string to a list
ALLOWED_ORIGINS = ALLOWED_ORIGINS.split(',')

# Initialize Flask application
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

# Define the database models


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
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
    Project_Name = db.Column(db.String(100))
    Task_Name = db.Column(db.String(100))
    Assigned_to = db.Column(db.String(100))
    Progress = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route('/companies', methods=['GET'])
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


@app.route('/financials/<int:company_id>', methods=['GET'])
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


@app.route('/extract', methods=['POST'])
def add_financials():
    try:
        # Get the file and company name from the request
        file = request.files.get('file')
        company_name = request.form.get('company_name')
        if file and company_name:
            # Convert the company name to lowercase and strip leading/trailing spaces
            company_name = company_name.lower().strip()

            # Check if the file has already been uploaded
            uploaded_file = UploadedFile.query.filter_by(
                filename=file.filename).first()
            if uploaded_file:
                # If the file has already been uploaded, return an error message
                return jsonify({'message': 'File has already been uploaded for another company', 'success': False}), 400

            # Check if the company already exists in the database
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                # If the company does not exist, create a new one
                company = Company(name=company_name)
                db.session.add(company)
                db.session.commit()

            # If the file has not been uploaded, create a new record
            uploaded_file = UploadedFile(
                filename=file.filename, company_id=company.id)
            db.session.add(uploaded_file)

            # Load the Excel file into a pandas DataFrame
            data = pd.read_excel(file, skiprows=5)

            # Extract only the required columns
            data = data[['Project Name', 'Task Name',
                         'Assigned to', 'Progress']]

            # Rename the columns to match the SQLAlchemy model
            data.columns = ['Project_Name',
                            'Task_Name', 'Assigned_to', 'Progress']

            # Save each row of data to the database
            for _, row in data.iterrows():
                # If the financial statement does not exist, create a new one
                record = FinancialStatement(
                    company_id=company.id, **row.to_dict())
                db.session.add(record)
            db.session.commit()

            return jsonify({'message': 'Financial statements added successfully', 'success': True}), 200
        else:
            return jsonify({'message': 'No file or company name provided', 'success': False}), 400
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database table
    app.run(debug=DEBUG)
