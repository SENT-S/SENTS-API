from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class ExcelData(db.Model):
    # Specify the table name
    __tablename__ = 'excel_data'

    # Define the columns for the table
    id = db.Column(db.Integer, primary_key=True)
    Project_Name = db.Column(db.String(100))
    Task_Name = db.Column(db.String(100))
    Assigned_to = db.Column(db.String(100))
    Progress = db.Column(db.String(50))

    # Method to convert a row of data into a dictionary
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route('/extract', methods=['POST'])
def extract_data():
    file = request.files.get('file')
    if file:
        try:
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
                record = ExcelData(**row.to_dict())
                db.session.add(record)
            db.session.commit()

            return jsonify({'message': 'Data extracted and saved successfully', 'success': True}), 200
        except Exception as e:
            return jsonify({'message': str(e), 'success': False}), 500
    else:
        return jsonify({'message': 'No file uploaded', 'success': False}), 400


@app.route('/retrieve', methods=['GET'])
def retrieve_data():
    try:
        # Retrieve all data from the database
        data = ExcelData.query.all()

        # Convert the data into a list of dictionaries
        response_data = [item.to_dict() for item in data]

        return jsonify({'message': 'Data retrieved successfully', 'success': True, 'data': response_data}), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


@app.route('/retrieve/<int:id>', methods=['GET'])
def retrieve_specific_data(id):
    try:
        # Retrieve the data with the given id
        data = ExcelData.query.get(id)

        # If the data does not exist, return an error message
        if data is None:
            return jsonify({'message': f'Data with id {id} not found', 'success': False}), 404

        # Convert the data into a dictionary
        response_data = data.to_dict()

        return jsonify({'message': 'Data retrieved successfully', 'success': True, 'data': response_data}), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database table
    app.run(debug=True)
