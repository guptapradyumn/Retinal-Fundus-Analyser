from flask import Flask, redirect, url_for, request ,render_template
from flask_mysqldb import MySQL
<<<<<<< HEAD
import label_image as model
import numpy as np
import cv2
from PIL import Image 
=======
import os
import calendar
import time
>>>>>>> ccb1df5634e3c91265db6ee4d2eb19bee79437a7

app = Flask(__name__) 

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='12345'
app.config['MYSQL_DB']='ianalyser'

app.config['UPLOAD_DIR']='static/images'
mysql= MySQL(app)

session={}
@app.route('/') 
def home(): 
	session={}
	return render_template('home.html')

@app.route('/create-account') 
def createAccount(): 
	return render_template('signup.html',message="")

@app.route('/validate',methods=['POST']) 
def validate(): 
	hospitalName = request.form['hospitalName']
	owner = request.form['owner']
	contact = request.form['contact']
	address = request.form['address']
	username = request.form['username']
	password = request.form['password']
	cur= mysql.connection.cursor()
	cur.execute("insert into hospital(name,owner,contact,address,username,password) values('"+hospitalName+"','"+owner+"','"+contact+"','"+address+"','"+username+"','"+password+"')")
	print(1)
	return redirect(url_for('home'))

@app.route('/home',methods = ['POST','GET']) 
def dashboard(): 
	if 'username' not in session :
		username = request.form['username']
		password = request.form['password']
		if (not username and not password):
				return redirect(url_for('home'))
		else:

			# print(username) 
			cur= mysql.connection.cursor()
			cur.execute("select * from hospital where username= '"+username+"' and password= '"+password+"'")
			data=cur.fetchall()
			if data:
				session['hospitalName']=data[0][1]
				session['username']=data[0][5]
				session['password']=data[0][6]


				print(session)
				return render_template('dashboard.html',data=session)
			else:
				return redirect(url_for('home'))

	else:
		return render_template('dashboard.html',data=session)



@app.route('/patient',methods=['POST','GET']) 
def patient(): 
	if('username' in session):
		if request.method=="POST":
			cusNumber = request.form['cusNumber']
			cur= mysql.connection.cursor()
			session['cusNumber']=cusNumber
			cur.execute("select * from patients where ID= '"+cusNumber+"'")
			data=cur.fetchall()
			if(data):
				return render_template('patient.html')
			else:
				return redirect(url_for('dashboard'))

		else:
			return render_template('patient.html')

	else:
		return redirect(url_for('home'))

@app.route('/register',methods=['POST'])
def register():
	if('username' in session):
		name = request.form['name']
		age = request.form['age']
		weight = request.form['weight']
		height = request.form['height']
		contact = request.form['contact']
		smoking = request.form['smoking']
		gender = request.form['gender']
		address = request.form['address']
		cur= mysql.connection.cursor()
		cur.execute("insert into patients(name,age,contact,address,weight,height,gender,smoking) values('"+hospitalName+"','"+age+"','"+contact+"','"+address+"','"+weight+"','"+height+"','"+gender+"','"+smoking+"')")
		return render_template('patient.html')

	else:
		return redirect(url_for('dashboard'))

@app.route('/upload', methods=['POST'])
def upload():
	file = request.files['file']
	filename = file.filename
	oldext=filename.split('.')[1]
	file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
	newName=str(session['cusNumber'])+str(calendar.timegm(time.gmtime()))
	os.rename(str(os.path.join(app.config['UPLOAD_DIR']))+'/'+filename, str(os.path.join(app.config['UPLOAD_DIR']))+'/'+newName + '.'+oldext)
	image_file=str(os.path.join(app.config['UPLOAD_DIR']))+'/'+newName + '.'+oldext
	# call function here
	return redirect(url_for('patient'))

if __name__ == '__main__': 
	app.run(debug = True) 