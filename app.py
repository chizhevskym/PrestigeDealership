from datetime import datetime,timedelta
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from gcsa.google_calendar import GoogleCalendar
from gcsa.attendee import Attendee
from gcsa.event import Event
from wtforms import Form, BooleanField, DateTimeField, StringField, TextField, SelectField, HiddenField, SubmitField, DateTimeField
from wtforms.validators import Length, DataRequired, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

app = Flask(__name__)

#for CSRF protection
app.config['SECRET_KEY'] = 'you-will-never-guess'

#connect to google calendar-uses ~\.config path for authentication
calendar = GoogleCalendar()

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
    def __init__(self, vin, model, make, year, mileage, exterior, interior, price, imageURL):
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
    employeeID = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(200))

 # constructor to initialize class
 #takes in self/this and all varables 
    def __init__(self,firstname,lastname):
        self.firstname = firstname
        self.lastname = lastname

#create model for customer
#intializes database
class Customer(db.Model):
    __tablename__ = 'Customer'
    customerID = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200))
    lastname = db.Column(db.String(200))
    zipcode = db.Column(db.String(5))

 # constructor to initialize class
 #takes in self/this and all varables 
    def __init__(self,firstname,lastname,zipcode):
        self.firstname = firstname
        self.lastname = lastname
        self.zipcode = zipcode

#create model for appointments\
#intializes database
class Appointment(db.Model):
    __tablename__ = 'Appointment'
    appointmentID = db.Column(db.Integer, primary_key=True)
    employeeID = db.Column(db.Integer)
    customerID = db.Column(db.Integer)
    vehicleID = db.Column(db.String(17))

 # constructor to initialize class
 #takes in self/this and all varables 
    def __init__(self,employeeID,customerID,vehicleID):
        self.employeeID = employeeID
        self.customerID = customerID
        self.vehicleID = vehicleID

# renders input form and validation
class AppointmentForm(FlaskForm): 
    customerfirst = StringField('customerfirstname', [DataRequired(), Length(max=200)])
    customerlast = StringField('customerlastname',[DataRequired(), Length(max=200)])
    zipcode = StringField('customerzipcode',[DataRequired(), Length(min = 5, max=5, message= 'Invalid Zip-Code')])
    employee = QuerySelectField('employee',[DataRequired()], query_factory=lambda: db.session.query(Employee).all(), get_label=lambda e: e.firstname + ' ' + e.lastname,allow_blank=True,blank_text='Select Employee')
    time= DateTimeField('time',[DataRequired("Year-Month-Day Hour:Min:Sec Format")])
    repeatcust = BooleanField('repeatcust')
    vin = HiddenField('vin', [DataRequired(), Length(max=17)])
    submit = SubmitField('Schedule Test Drive')

    # to validate that customer is in db
    def validate_repeatcust(form,field):
        if field.data == True and db.session.query(Customer).filter_by(firstname = form.customerfirst.data, lastname=form.customerlast.data, zipcode=form.zipcode.data).first() is None:
            raise ValidationError('You have not been here before (no matching customer in database)')

    # to validate that time is available in Google Calendar 
    def validate_time(form,field):
        # appointment length
        length=timedelta(hours = 2)
        start=field.data
        end=start + length
        # finds any conflicting events
        Events = calendar.get_events(time_min=start,time_max=end, order_by='updated', query="Employee="+form.employee.data.employeeID)
        for event in Events:
            raise ValidationError("Appointment Conflict! Employee is busy at that time, choose a different date or employee!")
        Events = calendar.get_events(time_min=start,time_max=end, order_by='updated', query="Vehicle="+form.vin.data)
        for event in Events:
            raise ValidationError("Appointment Conflict! Vehicle is needed at that time, choose a different date or vehicle!")


# Route for form / homepage
@app.route('/', methods=['GET'])
def index():
    cars = db.session.query(Vehicle).all()
    return render_template('home.html',inventoryList=cars)

@app.route('/index', methods=['GET', 'POST'])
def submit():
    #grab info from form
    #session.clear()
    form = AppointmentForm()
    vin = request.args.get('vin')
    vehicleInfo = db.session.query(Vehicle).filter_by(vin = vin).first()
    #form validation
    if form.validate_on_submit():
        print("validated")
        appt = None
        # appointment already exists
        try:
            custinfo = db.session.query(Customer).filter_by(firstname = form.customerfirst.data, lastname=form.customerlast.data, zipcode=form.zipcode.data).first()
            appt = db.session.query(Appointment).filter_by(employeeID=form.employee.data.employeeID,customerID=custinfo.customerID,vehicleID=form.vin.data).first()
            session['apptID']=appt.appointmentID
            print("Appointment Found")
        # appointment doesn't exist
        except:
            print("No appointment found")
            # edit previous appointment
            if 'apptID' in session:
                # find the old appointment and customer rows
                oldappt = db.session.query(Appointment).filter_by(appointmentID=session['apptID']).first()
                oldcust = db.session.query(Customer).filter_by(customerID=oldappt.customerID).first()
                # update customer info, keep same ID
                oldcust.firstname=form.customerfirst.data
                oldcust.lastname=form.customerlast.data
                oldcust.zipcode=form.zipcode.data
                custinfo=oldcust
                # update old appointment, keep same ID
                oldappt.employeeID=form.employee.data.employeeID
                oldappt.vehicleID=form.vin.data
                db.session.commit()
                print("Updated appointment")
            # new appointment creation
            else:
                print("new appt creation")
                #add new customer to db
                if form.repeatcust.data == False:
                    newcust= Customer(form.customerfirst.data,form.customerlast.data,form.zipcode.data)
                    db.session.add(newcust)
                    db.session.commit()
                #find customer in db
                custinfo = db.session.query(Customer).filter_by(firstname = form.customerfirst.data, lastname=form.customerlast.data, zipcode=form.zipcode.data).first()
                #add new appt to db
                newappt = Appointment(form.employee.data.employeeID,custinfo.customerID,form.vin.data)
                db.session.add(newappt)
                db.session.commit()
                #add new event to google calendar
                length=timedelta(hours = 2)
                start=form.time.data
                end=start + length 
                empattendee=Attendee(email="employee@fake.com",display_name=form.employee.data.employeeID, comment="Employee")
                custattendee=Attendee(email="customer@fake.com",display_name=custinfo.customerID, comment="Customer")
                vehattendee=Attendee(email="vehicle@fake.com",display_name=form.vin.data, comment="Vehicle")
                event = Event('Test-Drive', start=start, end=end, attendees=[empattendee,custattendee,vehattendee])
                calendar.add_event(event)
                session['apptID']=newappt.appointmentID
                print("Created appointment")
        finally: 
            return render_template('success.html', vehicleInfo=vehicleInfo,form=form)
    print("notvalidated")
    return render_template('index.html', vehicleInfo = vehicleInfo, form=form)

if __name__ == '__main__':
    app.run()