from flask import Blueprint, jsonify, request
from models import Company, FinancialStatement, UploadedFile, db
import pandas as pd

v1_Blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')


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
        stock_symbol = request.form.get('stock_symbol')
        sector = request.form.get('sector')
        stock_price = request.form.get('stock_price')
        gdp_change = request.form.get('gdp_change')

        # Check if all required fields are provided
        if not all([file, company_name, country_name, stock_symbol, sector, stock_price, gdp_change]):
            return jsonify({'message': 'All fields are required', 'success': False}), 400

        # Check if the provided data is of the correct type
        try:
            stock_price = float(stock_price)
            gdp_change = float(gdp_change)
        except ValueError:
            return jsonify({'message': 'Invalid data type provided for stock price or GDP change', 'success': False}), 400

        company_name = company_name.lower().strip()
        country_name = country_name.lower().strip()
        stock_symbol = stock_symbol.upper().strip()
        sector = sector.lower().strip()

        uploaded_file = UploadedFile.query.filter_by(
            filename=file.filename).first()
        if uploaded_file:
            return jsonify({'message': 'File has already been uploaded for another company', 'success': False}), 400

        company = Company.query.filter_by(name=company_name).first()
        if company:
            return jsonify({'message': 'Company already exists', 'success': False}), 400

        company = Company(name=company_name, country=country_name, stock_symbol=stock_symbol,
                          sector=sector, stock_price=stock_price, gdp_change=gdp_change)
        db.session.add(company)
        db.session.commit()

        uploaded_file = UploadedFile(
            filename=file.filename, company_id=company.id)
        db.session.add(uploaded_file)

        data = pd.read_excel(file, sheet_name='Snapshot')

        # Convert DataFrame to dictionary, skipping empty rows
        data_dict = data.dropna(how='all').to_dict('records')

        # Clean the data so that it can be stored in the database well for easy access in front end
        for row in data_dict:
            for key in row:
                if isinstance(row[key], float):
                    row[key] = str(row[key])
                if pd.isnull(row[key]):
                    row[key] = None

        # Save all rows of data to the database as an array of objects in a single record
        record = FinancialStatement(company_id=company.id, data=data_dict)
        db.session.add(record)
        db.session.commit()

        return jsonify({'message': 'Financial statements added successfully', 'success': True}), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500
