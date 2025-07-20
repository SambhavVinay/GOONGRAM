from flask import Flask, redirect, request, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import smtplib
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=r'C:\Users\Admin\OneDrive\Desktop\py\SQLAlchemyDatabase\Goongram\pass.env')

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

class Gooners(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    dateadded = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100))
    DOB = db.Column(db.String(100))

@app.route("/name",methods = ["POST","GET"])
def name():
    if request.method == "POST":
        name = request.form["name"]
        new_user = Gooners.query.order_by(Gooners.user_id.desc()).first()
        if new_user:
         new_name = Gooners(name = name)
         Gooners.name = name
         return redirect("/DOB")
        else:
            return "Error adding Gooner"
    return render_template("name.html")

@app.route("/DOB",methods = ["POST","GET"])
def DOB():
    if request.method == "POST":
        DOB = request.form["DOB"]
        new_user = Gooners.query.order_by(Gooners.user_id.desc()).first()
        if new_user: 
         new_DOB = Gooners(DOB = DOB)
         Gooners.DOB = DOB
         db.session.commit()
         return redirect("/dashboard")
        else:
            return"Failed to add DOB"
    return render_template("DOB.html")

@app.route("/intro")
def intro():
    return render_template("intro.html")

@app.route("/")
def home():
    return redirect("/intro")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_name = request.form["user_name"]
        user_password = request.form["user_password"]

        gooner = Gooners.query.filter_by(user_name=user_name, user_password=user_password).first()
        if gooner:
            client_message = f"Congrats {user_name}, Successful LOGIN onto GoonGram!"
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, user_name, client_message)
            return redirect("/name")
        else:
            return "Invalid Credentials (or) Gooner Not Registered !!!"

    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_name = request.form["user_name"]
        user_password = request.form["user_password"]

        if user_name and user_password:
            new_gooner = Gooners(user_password=user_password, user_name=user_name)
            db.session.add(new_gooner)
            db.session.commit()

        client_message = f"Dear {user_name}, Welcome to the GoonGram Community, GOON AWAY !"
        admin_message = f"Greetings BatMan, {user_name} has just taken part in the GoonGram initiative!"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, user_name, client_message)
        server.sendmail(EMAIL_USER, EMAIL_USER, admin_message)
        return redirect("/login")

    return render_template("register.html")

@app.route("/delete/<int:user_id>")
def delete(user_id):
    delete_gooner = Gooners.query.get_or_404(user_id)
    try:
        db.session.delete(delete_gooner)
        db.session.commit()
    except:
        return f"Failed to Delete Gooner id {user_id}"
    return redirect("/database")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/database")
def database():
    new_gooner = Gooners.query.order_by(Gooners.dateadded.desc()).all()
    return render_template("Database.html", new_gooner=new_gooner)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
