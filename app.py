from flask import Flask, redirect, url_for, request ,render_template


app = Flask(__name__) 

@app.route('/') 
def home(): 
	return render_template('home.html')

@app.route('/home') 
def dashboard(): 
	return render_template('dashboard.html')


@app.route('/patient') 
def patient(): 
	return render_template('patient.html')



if __name__ == '__main__': 
	app.run(debug = True) 