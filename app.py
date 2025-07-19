from flask import Flask, redirect, request, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Gooners.db'
db = SQLAlchemy(app)

class Gooners(db.Model):
 user_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
 user_name = db.Column(db.String(100), nullable=False)
 user_password = db.Column(db.String(100), nullable=False)
 dateadded = db.Column(db.DateTime, default = datetime.utcnow)

@app.route("/")
def home():
   return render_template("login.html")

@app.route("/login",methods=["POST","GET"])
def login():
   if request.method == "POST":
      user_name = request.form["user_name"]
      user_password = request.form["user_password"]
      
      gooner = Gooners.query.filter_by(user_name = user_name, user_password = user_password).first()
      if gooner:
         return redirect("/dashboard")
      else:
         return "Invalid Credentials (or) Gooner Not Registered !!!"
      
   return render_template("login.html")
  
@app.route("/register",methods=["POST","GET"])
def register():
   if request.method == "POST":
      user_name = request.form["user_name"]
      user_password = request.form["user_password"]
      
      new_gooner = Gooners(user_password = user_password, user_name = user_name)
      db.session.add(new_gooner)
      db.session.commit()

   return render_template("register.html")   

@app.route("/dashboard")
def dashboard():
   new_gooner = Gooners.query.group_by(Gooners.dateadded).all()
   return render_template("dashboard.html",new_gooner = new_gooner)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
