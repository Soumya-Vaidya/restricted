from flask import redirect, render_template, request, url_for

from app import app
from models import Company, db

from datetime import datetime

import pytz
from flask import send_file

IST = pytz.timezone("Asia/Kolkata")


with app.app_context():
    db.create_all()


@app.route("/test", methods=["GET", "POST"])
def test():
    return "hello"


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        # companies = Company.query.all()
        return render_template("home.html")
    elif request.method == "POST":
        return redirect(url_for("home"))


@app.route("/view", methods=["GET", "POST"])
def view_company():
    filter_active = request.args.get("active", default="True", type=str)

    if filter_active.lower() == "true":
        companies = Company.query.filter_by(active=True).all()
    elif filter_active.lower() == "false":
        companies = Company.query.filter_by(active=False).all()
    else:
        companies = Company.query.all()

    return render_template(
        "companies.html", companies=companies, filter_active=filter_active
    )


@app.route("/download-records", methods=["GET"])
def download_records():
    filter_active = request.args.get("active", default="True", type=str)

    if filter_active.lower() == "true":
        companies = Company.query.filter_by(active=True).all()
    elif filter_active.lower() == "false":
        companies = Company.query.filter_by(active=False).all()
    else:
        companies = Company.query.all()

    csv_content = "Company Name,Transaction Name,Start Date,End Date,Published Date,Comments,Date of Entry,Time of Entry,Date of End,Time of End\n"
    for company in companies:
        csv_content += f"{company.company_name},{company.transaction_name},{company.start_date},{company.end_date},{company.published_date},{company.comments},{company.date_of_entry},{company.time_of_entry},{company.date_of_end},{company.time_of_end}\n"

    with open("temp_records.csv", "w") as file:
        file.write(csv_content)

    return send_file(
        "temp_records.csv",
        as_attachment=True,
    )


@app.route("/add", methods=["GET", "POST"])
def add_company():
    if request.method == "GET":
        return render_template("add_company.html")
    elif request.method == "POST":
        company_name = request.form["company_name"]
        transaction_name = request.form["transaction_name"]
        start_date_str = request.form["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        comments = request.form["comments"]

        date_of_entry = datetime.now(IST).date()
        time_of_entry = datetime.now(IST).time()

        company = Company(
            company_name=company_name,
            transaction_name=transaction_name,
            start_date=start_date,
            comments=comments,
            date_of_entry=date_of_entry,
            time_of_entry=time_of_entry,
        )
        db.session.add(company)
        db.session.commit()
        print("Company added")
        return redirect(url_for("home"))


@app.route("/end", methods=["GET", "POST"])
def end_company():
    if request.method == "GET":
        companies = Company.query.filter_by(active=True).all()
        company_choices = [
            (company.company_id, f"{company.company_name} - {company.transaction_name}")
            for company in companies
        ]
        return render_template("end_company.html", company_choices=company_choices)
    elif request.method == "POST":
        company_id = request.form["company_id"]
        end_date_str = request.form["end_date"]
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        published_date_str = request.form["published_date"]
        published_date = datetime.strptime(published_date_str, "%Y-%m-%d").date()

        company = Company.query.get(company_id)
        if company:
            company.active = False
            company.end_date = end_date
            company.date_of_end = datetime.now(IST).date()
            company.time_of_end = datetime.now(IST).time()
            company.published_date = published_date
            db.session.commit()
            print("Company ended successfully")
            return redirect(url_for("home"))
        else:
            return "Company not found"
