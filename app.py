from flask import Flask, redirect, url_for, request ,render_template
from flask_mysqldb import MySQL

app = Flask(__name__) 

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='ianalyser'

mysql= MySQL(app)


@app.route('/') 
def home(): 
	return render_template('home.html')

@app.route('/create-account') 
def createAccount(): 
	return render_template('signup.html')

@app.route('/home') 
def dashboard(): 
	cur= mysql.connection.cursor()
	cur.execute("select * from hospital")
	data=cur.fetchall()
	print(data)
	return render_template('dashboard.html')


@app.route('/patient') 
def patient(): 
	return render_template('patient.html')



if __name__ == '__main__': 
	app.run(debug = True) 