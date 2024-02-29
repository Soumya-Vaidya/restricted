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


@app.route("/download", methods=["GET"])
def download():
    filter_active = request.args.get("active", default="True", type=str)

    if filter_active.lower() == "true":
        companies = Company.query.filter_by(active=True).all()
    elif filter_active.lower() == "false":
        companies = Company.query.filter_by(active=False).all()
    else:
        companies = Company.query.all()

    csv_content = "ISIN Number,Company Name,Transaction Type,Start Date,End Date,Published Date,Name of Person Informing, Contact Individuals,Comments,Date of Entry,Time of Entry,Date of End,Time of End\n"
    for company in companies:
        time_of_entry = str(company.time_of_entry)[0:8]
        time_of_end = str(company.time_of_end)[0:8]
        csv_content += f"{company.ISIN_number},{company.company_name},{company.transaction_type},{company.start_date},{company.end_date},{company.published_date},{company.person_of_contact},{company.person_email},{company.comments},{company.date_of_entry},{time_of_entry},{company.date_of_end},{time_of_end}\n"

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
        ISIN_number = request.form["ISIN_number"]
        company_name = request.form["company_name"]
        transaction_type = request.form["transaction_type"]
        person_of_contact = request.form["person_of_contact"]
        person_email = request.form["person_email"]
        start_date_str = request.form["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        comments = request.form["comments"]
        date_of_entry = datetime.now(IST).date()
        time_of_entry = datetime.now(IST).time()

        company = Company(
            ISIN_number=ISIN_number,
            company_name=company_name,
            transaction_type=transaction_type,
            person_of_contact=person_of_contact,
            person_email=person_email,
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
            (company.company_id, f"{company.company_name} - {company.transaction_type}")
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
