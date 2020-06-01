from flask import Flask, render_template
from flask_mysqldb import MySQL
#from crypt import methods
from flask.globals import request

app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']= 'password' #Enter password
app.config['MYSQL_DB']='flask_register' #Enter datbase name

mysql = MySQL(app);


@app.route('/', methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    username = request.form['user_name']
    useremail = request.form['your_email']
    userpass = request.form['password']
    cur.execute("INSERT INTO users(user_name,email_id,password) values(%s, %s, %s)",(username,useremail,userpass))
    mysql.connection.commit()
    cur.close()
    return render_template('success.html')

if __name__=='__main__':
    app.run(debug=True)
