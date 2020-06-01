import hashlib
import datetime
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request,render_template,session, redirect
from flask_pymongo import PyMongo
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
from random import randint
from builtins import int
#from crypt import methods
#from main import cursor

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

#DATABASE PART
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='utpala'
app.config['MYSQL_DB']='soteria1'

app.secret_key='cfa2d3d9fe912e6fe1a3536a78013183256876de9b44b8b0'

mysql = MySQL(app);
#MONGOPART
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)
#conn = mysql.connect()
#cur = mysql.connection.cursor()

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


def success_invest(acc_no, sender, invest, crypto, balance, old_balance):
    mail = Mail()
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = 'projectsoteria101@gmail.com'
    app.config["MAIL_PASSWORD"] = 'projectsoteria'
    mail.init_app(app)
    msg = Message("New investment successful", sender="Projectsoteria-support",recipients = [sender])
    warning = "\n\nNote : Never share your private key with anybody."
    sub = "Congratulations!!! You have successfully purchased cryptos. You've helped us in strengthening our digital money.\n\nTransaction summary: \n  "
    summary = "\nAccount number : "+ str(acc_no)+"\nAmount invested : "+ str(invest)+" INR"+"\nEquivavlent Cryptos:" + str(crypto)+"\nPrevious balance : "+str(old_balance)+"\nCurrent balance : "+ str(balance)+ warning
    msg.body=sub+summary
    mail.send(msg)
    return True
    
    
def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def trans_mail(sender_acc,sender,new_balance, receiver_acc,receiver,amount, new_balance_recv):
    mail = Mail()
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = 'projectsoteria101@gmail.com'
    app.config["MAIL_PASSWORD"] = 'projectsoteria'
    mail.init_app(app)
    summary = "\n\nTransaction summary :\n\n"+"Sent by : "+str(sender_acc)+"\nreceived by : "+ str(receiver_acc) +"\nAmount : "+ str(amount)+" \nCurrent balance : "
    
    msg = Message("Account Credited", sender="Projectsoteria-support",recipients = [receiver])
    warning = "\n\nNote : Never share your private key with anybody."
    msg.body = " Your account has been credited by amount  " + str(amount)+summary+ str(new_balance_recv) +warning
    mail.send(msg)
    msg = Message("Account Debited", sender="Projectsoteria-support",recipients = [sender])
    warning = "\n\nNote : Never share your private key with anybody."
    msg.body = "Your account has been debited by amount  " +str(amount)+ summary +str(new_balance)+ warning
    mail.send(msg)
    return True

class block0(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            
            'timestamp': time(),
            'date': datetime.datetime.now(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(mongo.db.blockchain.find().sort([('_id',-1)]).limit(1))
        }

        # Reset the current list of transactions
        self.current_transactions = []

        mongo.db.blockchain.insert(block)
        return block

    def new_transaction(self, sender, recipient,amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        #mongo.db.transactions.insert(self.current_transactions)

    @property
    def last_block(self):
        return mongo.db.blockchain.find().sort([('_id',-1)]).limit(1)

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


	

@app.route('/',methods=['GET','POST'])
def home_page():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    error = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'user_name_1' in request.form and 'password_1' in request.form:
        # Create variables for easy access
        username = request.form['user_name_1']
        password = request.form['password_1']
        # Check if account exists using MySQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users_details WHERE user_name = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cur.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            return redirect('/welcome')
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', error=error)


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
    acc_no = 0
    
    for x in result:
        acc_no = x[0]
    cur.close()
    status = sendMail(username, useremail, acc_no, key)
    
    if(status):
        return render_template("success.html")
    return render_template('login.html')


@app.route('/index',methods=['GET'])
def index_page():
    return render_template('index_trial.html')

@app.route('/welcome', methods=['GET','POST'])
def welcome():
    return render_template('Welcome_page.html')

@app.route('/transfer_page')
def transfer_page():
    return render_template('finalt.html')

@app.route('/transaction', methods=['GET','POST'])
def transaction():
    sender=str(request.form["sender"])
    receiver=request.form["receiver"]
    amount=request.form["amount"]
    pin=request.form["pin"]
    amount=float(amount)	
    cur = mysql.connection.cursor()
    userName = session['username']
    cur.execute("select * from users_details where acc_no = %s and acc_no!=%s",(receiver,sender))
    validate_receiver = cur.fetchone()
    if amount < 0:
        err = "Oops !! Invalid amount. Please enter valid amount"
        return render_template("Error_trans.html",error=err)
    
    if not validate_receiver:
        err="Oops!! Invalid receiver. Please enter valid account number"
        return render_template("Error_trans.html",error=err)
    cur.execute("select * from users_details where acc_no = %s or user_name= %s",(sender,userName))
    result = cur.fetchall()
    for x in result:
        balance = x[5]
    if(balance == None):
        balance = 0;
        
    if float(balance) <= float(amount):
        error = "Oops!! Insufficient balance.\n\n PLease go to 'Account summary section to check your balance"
        return render_template("Error_trans.html",error=error)
        
    key = 0
    for x in result:
        key=x[4]
    if key==pin:
        block_cur=block0()
        last_block = block_cur.last_block
        proof = block_cur.proof_of_work(last_block)
        block_cur.new_transaction(
	        sender=sender,
	        recipient=receiver,
	        amount=amount,
	    )
        previous_hash = block_cur.hash(str(last_block))
        block = block_cur.new_block(proof, previous_hash)
        for x in result:
            old_balance=float(x[5])
            sender_email=x[2]
            
        cur.execute("select * from users_details where acc_no=%s and acc_no!=%s",(receiver,sender))
        result = cur.fetchall()
        
        for x in result:
            receiver_email=x[2]
            old_balance_recv = float(x[5]) 	
        
        new_balance= round(old_balance-amount,3)
        new_balance_recv = round(old_balance_recv+amount,3)
        cur.execute("update users_details set balance = %s where acc_no=%s",(new_balance,sender))
        cur.execute("update users_details set balance = %s where acc_no=%s",(new_balance_recv,receiver))
        
        mysql.connection.commit()
        trans_mail(sender,sender_email,new_balance,receiver,receiver_email,amount,new_balance_recv)
        
        data = [
            {
                'sender':sender,
                'receiver': receiver,
                'amount':amount,
                'balance': new_balance
            }]
        return render_template('success_trans.html', data = data)
    else:
        err = " Oops ! Incorrect pin entry.\n\n Check your earlier emails for your private key :)"
        return render_template("Error_trans.html", error = err)
    
@app.route('/invest', methods=['GET','POST'])
def invest():
    return render_template('invest.html')


@app.route('/trial', methods=['GET','POST'])
def trial():
    return render_template('trial.html')

@app.route('/payment' , methods=['GET','POST'])
def pay():
    rupee= request.form["amount"]
    session['amount']= rupee
    return render_template('pay.html', data = rupee)

@app.route('/accountSummary', methods=['GET','POST'])
def acc_summ():
    userName= session['username']
    acc_no = session['id']
    cur = mysql.connection.cursor()
    cur.execute('select * from users_details where user_name=%s and acc_no = %s',(userName,acc_no))
    results= cur.fetchall()
    for x in results:
        balance = x[5];
        email = x[2];
        
    acc_data = {
        'acc_no': acc_no,
        'username':userName,
        'email': email,
        'balance': balance
        }
    
    #acc_trans = mongo.db.blockchain.find({'transactions':{$or :[{'sender':acc_no},{'receiver': acc_no}})
    acc_trans = mongo.db.blockchain.find({'$or': [{"transactions.sender" : str(acc_no)},{"transactions.recipient":str(acc_no)}]}).sort([('_id',-1)])
    return render_template('finalas.html', acc_details=acc_data,trans = acc_trans)

@app.route('/summary',methods=['GET','POST'])
def summ():
    return render_template('summary.html')

@app.route('/validatePayment',methods=['GET','POST'])
def validatePayment():
    nameCard = request.form['name_on_card']
    card_no = request.form['card_no']
    cvc = request.form['cvc']
    exp_month = request.form['exp_month']
    exp_year = request.form['exp_year']
    amount= session['amount']
    cur = mysql.connection.cursor()
    cur.execute('select * from card_details where acc_no=%s and acc_no=%s',(str(session['id']),str(session['id'])))
    validate_card = cur.fetchone()
    if validate_card:
        cur.execute('update card_details set name_on_card =%s, card_no=%s, cvc = %s, exp_date=%s, exp_year=%s where acc_no=%s',(nameCard,card_no,cvc,exp_month,exp_year,session['id']))    
    
    else:
        cur.execute('insert into card_details values(%s,%s,%s,%s,%s,%s)',(session['id'],nameCard,card_no,cvc,exp_month,exp_year))
        
    crypto = round(float(amount)/float(1298),2)
    cur.execute('select * from users_details where acc_no=%s and user_name=%s',(session['id'],session['username']))
    result = cur.fetchall()
    for x in result:
        balance = x[5]
        email= x[2]
        
    if balance == None :
        balance = 0;
    old_balance = balance
    balance= round(float(balance)+ float(crypto),2)
    cur.execute('update users_details set balance=%s where acc_no=%s',(balance,session['id']))
    mysql.connection.commit()
    data={ 'rupee' : amount, 'crypto':crypto, 'balance':balance }
    success_invest(session['id'], email, amount, crypto, balance, old_balance)
    return render_template('success_invest.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)	