from sqlalchemy import DateTime, Date, Time

from app import db


class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(), nullable=False)
    transaction_name = db.Column(db.String(), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date)
    comments = db.Column(db.String())
    active = db.Column(db.Boolean, default=True)
    published_date = db.Column(db.Date)
    date_of_entry = db.Column(Date)
    time_of_entry = db.Column(Time)
    date_of_end = db.Column(DateTime)
    time_of_end = db.Column(Time)
