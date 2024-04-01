from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    country = db.Column(db.String(100))
    stock_symbol = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    stock_price = db.Column(db.Float)
    gdp_change = db.Column(db.Float)
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
