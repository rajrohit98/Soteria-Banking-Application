from flask import Flask, render_template,session,redirect
from flask_mysqldb import MySQL
#from crypt import methods
from flask.globals import request
from flask_mail import Mail,Message
from random import randint


app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='utpala'
app.config['MYSQL_DB']='flask_register'

app.secret_key='cfa2d3d9fe912e6fe1a3536a78013183256876de9b44b8b0'

mysql = MySQL(app);
#cursor = mysql.connection.cursor()

def sendMail(user_name,user_email,user_acc,user_key):
    mail = Mail()
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = 'projectsoteria101@gmail.com'
    app.config["MAIL_PASSWORD"] = 'projectsoteria'
    mail.init_app(app)
    email = user_email
    msg = Message("Account Created", sender="Projectsoteria-support",recipients = [email])
    warning = "Note : Never share your private key with anybody."
    msg.body = " Congratulations! Your account has been created!!!"+"\n\nUsername:"+str(user_name)+"\nAccount number : "+ str(user_acc)+"\nPrivate Key : "+str(user_key)+"\n\n"+warning
    mail.send(msg)
    return True    

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    username = request.form['user_name']
    useremail = request.form['your_email']
    userpass = request.form['password']
    cur.execute("select * from users_details where user_name=%s or email_id=%s",(username,useremail))
    if(cur.rowcount!=0):
        return render_template('login.html')
    key = randint(1000,9999)
    key = str(key)
    cur.execute("INSERT INTO users_details(user_name,email_id,password,secret_key) values(%s, %s, %s, %s)",(username,useremail,userpass,key))
    mysql.connection.commit()
    cur.execute("select * from users_details where user_name=%s or email_id=%s",(username,useremail))
    result = cur.fetchall()
    acc_no = 0;
    for x in result:
        acc_no = x[0]
    cur.close()
    
    status = sendMail(username, useremail, acc_no, key)
    if(status):
        return render_template("success.html")
    return render_template('login.html')
    
@app.route('/login',methods=['POST']) 
def login():
    username = request.form['user_name_1']
    user_acc = request.form['acc_no']
    user_pass = request.form['password_1']
    #user_acc = int(user_acc)
    #user_acc= bytes_to_int(user_acc)
    cur = mysql.connection.cursor()
    cur.execute('select * from users_details where acc_no=%s and user_name=%s and password=%s',(user_acc,username,user_pass))
    if(cur.rowcount!=0):
        session['user']=username
        session['acc_no']=user_acc
        return redirect('/welcome')
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


    
    

   
if __name__=='__main__':
    app.run(debug=True)
