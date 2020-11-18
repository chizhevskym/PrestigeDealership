from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ENV = 'dev'
ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/dealership'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://eferowmoegoito:e0405aba75574cbb9d8fa5d3fd236ea91512c755e7e5a739e4b3132d9598bd77@ec2-3-220-98-137.compute-1.amazonaws.com:5432/d17l6nv22ftldo'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#create db object and pass app to qquery db
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

# constructor to intiazie class
#takes in self/this and all varables expect id
    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

# Rotue for form / homepage
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def index_func():
    if request.method == 'POST':
        return redirect(url_for('index.html'))
    return render_template('index.html')

# verify method is post
# return form data as variables
#print data in console
#render sucess page if true

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        print(customer, dealer, rating, comments)
        # if form is empty, display alert
        if customer == '' or dealer =='':
            return render_template('index.html',message='Please enter required fields')
        
        #Queries
        #Check customer doesnt already exist
        #grab data being passed into db
        #add data to db, commit to db, render success
        #if customer exists, render index with message
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback')

if __name__ == '__main__':
    app.run()