'''
Created on 30-Mar-2020

@author: me
'''
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request,session,render_template
from flask_pymongo import PyMongo
from flask_mysqldb import MySQL 
from flask_mail import Mail, Message
from random import randint

app = Flask(__name__)

#DATABASE PART
mysql = MySQL()
app.secret_key = 'rootpasswordgiven'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'rootpasswordgiven'
app.config['MYSQL_DATABASE_DB'] = 'soteria1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#MONGOPART
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)

conn = mysql.connect()
cursor =conn.cursor()

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

class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
           
            'timestamp': time(),
            'transactions': str(self.current_transactions),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(mongo.db.blockchain.find().sort({'_id':-1}))
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount,date,time):
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
            'date' : date,
            'time': time
        })
       
        #mongo.db.transactions.insert(self.current_transactions)

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return mongo.db.blockchain.findone().sort({'_id':-1})

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    error = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM customer WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[2]
            # Redirect to home page
            return render_template('start.html')
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect user name/password!'
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
    acc_no = 0;
    for x in result:
        acc_no = x[0]
    cur.close()
   
    status = sendMail(username, useremail, acc_no, key)
    if(status):
        return render_template("success.html")
    return render_template('login.html')

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.form=='POST':
        sender=request.form["sender"]
        receiver=request.form["receiver"]
        amount=request.form["amount"]
        current_transactions.append({
            'sender': sender,
            'recipient': receiver,
            'amount': amount,
            })


if __name__ == '__main__':
    app.run(debug=True)