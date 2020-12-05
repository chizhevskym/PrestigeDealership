from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'dev'
#ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Admin1998@localhost:5432/dealershipDB'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nipjuuzixjcifo:de170cd30d844ed34cfad75a81f8bc08b06dcaaf817887a839563271f27c8087@ec2-23-23-88-216.compute-1.amazonaws.com:5432/dfb62v7qlveoi8'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#create db object and pass app to query db
db = SQLAlchemy(app)

#create model for feedback form
#intializes database
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

 # constructor to initialize class
 #takes in self/this and all varables expect id
    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

#create model for vehicle
#intializes database
class Vehicle(db.Model):
    __tablename__ = 'Vehicle'
    vin = db.Column(db.String(17), primary_key=True)
    model = db.Column(db.String(200))
    make = db.Column(db.String(200))
    year = db.Column(db.String(5))
    mileage = db.Column(db.Float)
    exterior = db.Column(db.String(200))
    interior = db.Column(db.String(200))
    price = db.Column(db.Float)
    imageURL = db.Column(db.String(400))

 # constructor to initialize class
 #takes in self/this and all varables 
    def __init__(vin, model, make, year, mileage, exterior, interior, price, imageURL):
        self.vin = vin
        self.model = model
        self.make = make
        self.year = year
        self.mileage = mileage
        self.exterior = exterior
        self.interior = interior
        self.price = price
        self.imageURL = imageURL

#create model for employee
#intializes database
class Employee(db.Model):
    __tablename__ = 'Employee'
    employeeID = db.Column(db.String(200), primary_key=True)
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(200))

 # constructor to initialize class
 #takes in self/this and all varables 
    def __init__(employeeID,firstname,lastname):
        self.employeeID = employeeID
        self.firstname = firstname
        self.lastname = lastname

# Route for form / homepage
@app.route('/', methods=['GET'])
def index():
    cars = db.session.query(Vehicle).all()
    return render_template('home.html',inventoryList=cars)

@app.route('/index', methods=['GET'])
def index_func():
    vin = request.args.get('vin')
    vehicleInfo = db.session.query(Vehicle).filter_by(vin = vin).first()
    employeeList = db.session.query(Employee).all()
    return render_template('index.html', vehicleInfo = vehicleInfo, employeeList= employeeList)

# verify method is post
# return form data as variables
#print data in console
#render sucess page if true

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customerfirst = request.form['customerfirstname']
        customerlast = request.form['customerlastname']
        zipcode = request.form['customerzipcode']
        employee = request.form['employee']
        repeatcust = request.form['repeatcust']
        vin = request.form['vin']
        print(customerfirst, customerlast, zipcode, employee, repeatcust, vin)
        return render_template("success.html")

if __name__ == '__main__':
    app.run()