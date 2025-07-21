from flask import Flask, redirect, request, render_template,session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import smtplib
from dotenv import load_dotenv
import os
from flask import jsonify

load_dotenv(dotenv_path=r'C:\Users\Admin\OneDrive\Desktop\py\SQLAlchemyDatabase\Goongram\pass.env')

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = "NiggaBalls"

class Gooners(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    dateadded = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100))
    DOB = db.Column(db.String(100))

@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "user_id" not in session:
        return redirect("/login")
    user = Gooners.query.get(session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/name", methods=["POST", "GET"])
def name():
    if request.method == "POST":
        name = request.form["name"]
        user = Gooners.query.get(session["user_id"])
        if user:
            user.name = name  
            db.session.commit()
            return redirect("/DOB")
        else:
            return "Error adding name"
    return render_template("name.html")


@app.route("/DOB", methods=["POST", "GET"])
def DOB():
    if request.method == "POST":
        dob = request.form["DOB"]
        user = Gooners.query.get(session["user_id"])
        if user:
            user.DOB = dob  
            db.session.commit()
            return redirect("/dashboard")
        else:
            return "Failed to add DOB"
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
            session["user_id"] = gooner.user_id
            client_message = f"Congrats {user_name}, Successful LOGIN onto GoonGram!"
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, user_name, client_message)
            if gooner.name and gooner.DOB:
                return redirect("/gooners")
            else:
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

@app.route("/search",methods = ["POST","GET"])
def search():
    if request.method == "POST":
       name = request.form["name"]
       search_name = Gooners.query.filter(Gooners.name.ilike(f"%{name}%")).all()
       return render_template("search_results.html",search_name = search_name,query=name)
    return render_template("search.html")

@app.route("/suggest") #VIBECODED   
def suggest():
    query = request.args.get("query", "")
    results = Gooners.query.filter(Gooners.name.ilike(f"{query}%")).limit(5).all()
    suggestions = [{"name": u.name, "user_name": u.user_name} for u in results]
    return jsonify(suggestions)

@app.route("/profile/<int:user_id>")
def profile_open(user_id):
    user = Gooners.query.get_or_404(user_id)
    return render_template("profile.html",user = user)

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

@app.route("/gooners")
def gooners():
    present = Gooners.query.order_by(Gooners.dateadded.desc()).all()
    return render_template("present.html", present = present)

 
@app.route("/database")
def database():
    new_gooner = Gooners.query.order_by(Gooners.dateadded.desc()).all()
    return render_template("Database.html", new_gooner=new_gooner)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
