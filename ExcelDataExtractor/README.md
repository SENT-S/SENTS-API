# Flask API for Financial Statements

This is a Flask API that allows you to upload financial statement data for different companies and retrieve it.

## Installation

First, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/yourrepository.git
```

Start a virtual environment with in the directory of the Excel Data Extractor. this can be done by running the following command:

```bash
python -m venv env
```

Activate the environment by running the following command:

Windows Machine

```bash
source env/bin/activate
```

Mac && Linux

```bash
env\Scripts\activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

## Usage

Start the server:

```bash
python app.py
```

Endpoints

[POST] /extract
Upload a financial statement for a company.

Request parameters:

- file: The financial statement file to be uploaded.
- company_name: The name of the company.

Response: A message indicating whether the financial statements were added successfully.

[GET] /financials/int:company_id
Retrieve the financial statements for a given company.

Request parameters:

- company_id: The ID of the company.

Response: The financial statements for the company.

[GET] /companies
Retrieve all companies.

Response: A list of all companies.

## Docker

docker-compose build
docker-compose up
docker-compose down
docker-compose logs
