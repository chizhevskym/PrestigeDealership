from flask import Flask, render_template, request
app = Flask(__name__)

# Rotue for form / homepage
@app.route('/')
def index():
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
        return render_template('success.html')

if __name__ == '__main__':
    app.debug = True
    app.run()