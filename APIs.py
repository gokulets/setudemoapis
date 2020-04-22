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

