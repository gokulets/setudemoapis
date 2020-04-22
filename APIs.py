from flask import Flask, request, jsonify, make_response   
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid 
import jwt
import datetime
from functools import wraps
import sys

app = Flask(__name__) 


app.config['SECRET_KEY']='S12E23ET993U'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite://///Ubuntu/Home/Project/SetuAPI.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True 

db = SQLAlchemy(app)   

class Users(db.Model):  
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.Integer)  
  name = db.Column(db.String(50))
  password = db.Column(db.String(50))
  admin = db.Column(db.Boolean)

class Customer(db.Model):  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  customerID = db.Column(db.String(15))
  idType = db.Column(db.String(15))

class Bills(db.Model):  
   id = db.Column(db.Integer, primary_key=True)
   generated_on = db.Column(db.String(20),unique=False, nullable=False)   
   recurrence = db.Column(db.String(10),nullable=True)
   displayName = db.Column(db.String(20),nullable=True)
   amountExactness = db.Column(db.String(10),nullable=True)
   amount = db.Column(db.Integer,nullable=True)
   customerIDType = db.Column(db.String(15),nullable=True)
   customerID = db.Column(db.String(20),nullable = False)
   customerName = db.Column(db.String(20),nullable = True)
   fetchStatus = db.Column(db.Boolean) 

class Receipts(db.Model):  
   id = db.Column(db.Integer, primary_key=True)
   generated_on = db.Column(db.String(20),unique=True, nullable=False)   
   billerID = db.Column(db.Integer,unique=True, nullable=False)
   platformBillID = db.Column(db.String(20),unique=False, nullable=False)
   platformTransactionRefID = db.Column(db.String(20),unique=False, nullable=False)   
   uniquePaymentRefID = db.Column(db.String(20),unique=False, nullable=False) 
   amountPaid = db.Column(db.Integer, nullable=True)
   billAmount = db.Column(db.Integer, nullable=True)


def token_required(f):  
    @wraps(f)  
    def decorator(*args, **kwargs):

       token = None 
    
       if 'Authorization' in request.headers:
           token = request.headers['Authorization'].split(" ")[1]

       if not token:  
          return jsonify({'message': 'a valid token is missing'})   


       try:  
          data = jwt.decode(token, app.config['SECRET_KEY']) 
          print(data)
          current_user = Users.query.filter_by(public_id=data['public_id']).first()  
          print(current_user)
       except:  
          return jsonify({'message': 'token is invalid'})  

       return f(current_user, data['public_id'], *args,  **kwargs)  
    return decorator 

@app.route('/register', methods=['GET', 'POST'])
def signup_user():  
 data = request.get_json()  

 hashed_password = generate_password_hash(data['password'], method='sha256')
 
 new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False) 
 db.session.add(new_user)  
 db.session.commit()    

 return jsonify({'message': 'registered successfully'})   


@app.route('/login', methods=['GET', 'POST'])  
def login_user(): 
 
  auth = request.authorization   

  if not auth or not auth.username or not auth.password:  
     return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

  user = Users.query.filter_by(name=auth.username).first()   
     
  if check_password_hash(user.password, auth.password):  
     token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30)}, app.config['SECRET_KEY'])  
     data = jwt.decode(token, app.config['SECRET_KEY']) 
     print(data)

     return jsonify({'token' : token.decode('UTF-8')}) 

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/',methods=['GET','POST','PUT','DELETE'])
def hello():

 return jsonify({'ServerStatus':'ON','Message':'Hello World'})

@app.route('/user', methods=['GET'])
def get_all_users():  
   
   users = Users.query.all() 

   result = []   

   for user in users:   
       user_data = {}   
       user_data['public_id'] = user.public_id  
       user_data['name'] = user.name 
       user_data['password'] = user.password
       user_data['admin'] = user.admin 
       
       result.append(user_data)   

   return jsonify({'users': result})  


@app.route('/bills', methods=['POST'])
@token_required
def create_bill(current_user,public_id):
   
   data = request.get_json() 
   
   customer = data['customer']
   customerName = customer['name']
   customerIDType = customer['idtype'] 
   customerID = customer['id']


   customer = Customer.query.filter_by(customerID=customerID).first()   
   if not customer:   
       new_customer = Customer(name=customerName,idType=customerIDType,customerID=customerID)
       db.session.add(new_customer)
       db.session.commit()

   print('the values are'+customerName,customerIDType,customerID)

   bills = data['bills']
   recurr = ''
   amountExactness = ''
   displayName = ''
   amount = ''

   now = datetime.datetime.utcnow()
   current_time = now.strftime ("%Y-%m-%dT%H:%M:%S%Z")

   print('sssd'+current_time)

   for bill in bills:
     recurr = bill['recurrence']
     amountExactness = bill['amountExactness']
     aggregates = bill['aggregates']
     total = aggregates['total']
     displayName = total['displayName']
     amountSec = total['amount']
     amount = amountSec['value']
     print('the second values are'+recurr,amountExactness,displayName,amount)
   
     new_bill = Bills(generated_on=current_time,recurrence=recurr,displayName=displayName,amountExactness=amountExactness,amount=int(amount),customerIDType=customerIDType,customerID=customerID,customerName=customerName,fetchStatus=True)  
     db.session.add(new_bill)   
     db.session.commit()   
   

   return jsonify({'message' : 'new bill has been created'})

