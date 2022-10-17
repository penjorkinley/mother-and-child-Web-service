import datetime
import flask
import json 
import requests
import flask_mail
from email.policy import default
from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail


with open('templates\config.json', 'r') as c:
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__)

#To send mail to your account
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)
#database for contacts
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique= False, nullable=False)
    email = db.Column(db.String(20),  nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(120), nullable=False) 
#database for appointment
class Appointment(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique= False, nullable=False)
    email = db.Column(db.String(20),  nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    department = db.Column(db.String(12), nullable=True)
    dzongkhag = db.Column(db.String(12), nullable=True)
    message = db.Column(db.String(120), nullable=False) 
#database for Posts
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


#function for Health News API
def healthapi():
    
    url = ('https://newsapi.org/v2/top-headlines?'
        'country=us&'
        'category=health&'
        'apiKey=fd043899448f4e429d3d038a4cbd9829')
    response = requests.get(url)
    return (response.json()['articles']) 
news=healthapi()
params['data']=news

#function for Newsletter
def subscribe_user(email, use_group_email, api_key):
    resp = requests.post("https://api.mailgun.net/v3/lists/{user_group_email}/members",
                        auth = ("api", api_key),
                        data = {"subscribed": True, 
                        "address": email}
                        )
    print(resp.status_code)                    
    return resp



 
#Routes 
@app.route('/')
def home():
    #to render index.html
    return render_template("index.html", params=params)

@app.route('/index.html')
def homePage():
    #to render index.html
    return render_template("index.html", params=params)

@app.route('/newsletter')
def newsletter():
    if request.method == "POST":
        email = request.form.get('email')

        subscribe_user(email = email, 
                       user_group_email = "newsletter@sandbox5626ae924ded48b2a18eb4278559e481.mailgun.org",
                       api_key="b0ed5083-d1b04b6f "
          )
    return render_template("layout.html", params=params)


@app.route('/index.html#about')
def aboutUs():
    return render_template("index.html", params=params)

@app.route('/index.html#services')
def services():
    return render_template("index.html", params=params)

@app.route('/index.html#departments')
def departments():
    return render_template("index.html", params=params)

@app.route('/index.html#doctors')
def doctors():
    return render_template("index.html", params=params)

@app.route('/contact', methods= ['GET','POST'])
def contact():
    #to submit data to the contact table of mch database
    if(request.method=='POST'):
        '''Fetch data and add it to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message= request.form.get('message')
        entry = Contacts(name=name,email=email,subject=subject,message=message)
        
        db.session.add(entry)
        db.session.commit()
        #To receieve email when someone submits contact form
        mail.send_message('Message From Contact: ' + name,
                         sender=email,
                         recipients = [params['gmail-user']],
                         body = "Contacted by"+ "\n" +"Patient name:" + name  + "\n" +"Message:" + message + "\n" + "Email: " + email 
        )
    return render_template("contact.html", params=params)

@app.route('/appointment', methods= ['GET','POST'])
def appointment():
    #to submit data to the appointment table of mch database
    if(request.method=='POST'):
        '''Fetch data and add it to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('date')
        department = request.form.get('department')
        dzongkhag = request.form.get('dzongkhag')
        message= request.form.get('message')
        entry = Appointment(name=name,email=email,phone=phone,date=datetime.now(),department=department,dzongkhag=dzongkhag,message=message)
        
        db.session.add(entry)
        db.session.commit()
        #To receieve email when someone books an appointment 
        mail.send_message('Appointment Booking ' + name,
                         sender=email,
                         recipients = [params['gmail-user']],
                         body = "Appointment has been booked by:"+ "\n" +"Patient name:" + name + "\n" + "Date:"+ date + "\n" +"Patient's Note:" + message
        )
    return render_template("appointment.html", params=params)

@app.route('/educationalContent')
def educationalContent():
    return render_template("educationalContent.html", params=params)



@app.route('/innerpage')
def innerPage():
    #to render index.html
    return render_template("inner-page.html", params=params)

#to run the web app
if __name__ == "__main__":
    app.run(debug=True, port=8000) #To change port number