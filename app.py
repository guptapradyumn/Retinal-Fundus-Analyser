from flask import Flask, redirect, url_for, request ,render_template
from flask_mysqldb import MySQL
import os
import calendar
import time
import scripts.label_image as model
import skel as sk
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
	mysql.connection.commit()
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
			cur.execute("SELECT images.name , reports.glaucoma , reports.diabetes , reports.edema , reports.remark from images, reports where images.ID = reports.imageID and images.patientID="+session['cusNumber'])
			data1=cur.fetchall()
			#print(data2)
			if(data or data1):
				return render_template('patient.html',data=data1)
			else:
				return redirect(url_for('dashboard'))

		else:
			cusNumber=session['cusNumber']
			cur= mysql.connection.cursor()
			cur.execute("select * from patients where ID= '"+cusNumber+"'")
			data=cur.fetchall()
			cur.execute("SELECT images.name , reports.glaucoma , reports.diabetes , reports.edema , reports.remark from images, reports where images.ID = reports.imageID and images.patientID="+session['cusNumber'])
			data1=cur.fetchall()
			return render_template('patient.html',data=data1)

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
		mysql.connection.commit()
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
	result=[]
	sk.convert(image_file)
	glaucoma_graph="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/glaucoma_graph.pb"
	galucoma_label="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/glaucoma_labels.txt"
	edema_graph="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/edema_graph.pb"
	edema_label="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/edema_labels.txt"
	daibetic_graph="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/diabetic_graph.pb"
	daibetic_label="/home/akshay/Documents/BE_PROJECT/Retinal-Fundus-Analyser/tf_files/diabetic_labels.txt"

	glaucoma_output=model.start(image_file,glaucoma_graph,galucoma_label)
	edema_output=model.start(image_file,edema_graph,edema_label)
	daibetic_output=model.start(image_file,daibetic_graph,daibetic_label)
	for i in glaucoma_output:
		if i[1]=="glaucoma":
			result.append(i[0])
	
	maxi=0
	label=""
	for i in edema_output:
		if(i[0]>maxi):
			maxi=i[0]
			label=i[1]
	result.append(label)

	maxi1=0
	label1=""
	for i in daibetic_output:
		if(i[0]>maxi1):
			maxi1=i[0]
			label1=i[1]
	result.append(label1)
	cur= mysql.connection.cursor()
	query="insert into images(name,patientId) values ( '"+image_file+"',"+session['cusNumber']+")"
	cur.execute(query)
	result.append(cur.lastrowid)
	
	mysql.connection.commit()

	cusNumber=session['cusNumber']
	cur.execute("select * from patients where ID= '"+cusNumber+"'")
	data=cur.fetchall()
	cur.execute("SELECT images.name , reports.glaucoma , reports.diabetes , reports.edema , reports.remark from images, reports where images.ID = reports.imageID and images.patientID="+session['cusNumber'])
	data1=cur.fetchall()
	
	return render_template('patient.html',data_analyzed=result,data=data1)


@app.route('/saveData', methods=["POST"])
def saveData():
	remark="Not given"
	glaucoma=request.form['glaucoma']
	edema=request.form['edema']
	diabetes=request.form['diabetes']
	remark=request.form['remark']
	imageId=request.form['imageId']

	cur= mysql.connection.cursor()
	query="insert into reports(imageID,glaucoma,edema,diabetes,remark) values ( "+imageId+",'"+glaucoma+"','"+edema+"','"+diabetes+"','"+remark+"')"
	print(query)
	cur.execute(query)
	cur.close()
	mysql.connection.commit()
	return redirect(url_for('patient'))

if __name__ == '__main__': 
	app.run(debug = True) 