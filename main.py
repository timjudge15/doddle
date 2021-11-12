from collections import Counter
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
import os
import json
import secrets
import scripts.userdata.transactions
import scripts.userdata.abis
import requests
import stripe

secret_key = secrets.token_hex(16)

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
stripe.api_key = 'sk_test_26PHem9AhJZvU623DfE1x4sd'

def num_there(string):
    state = any(i.isdigit() for i in string)
    return state

def usdcabi():
    abi = scripts.userdata.abis.usdc()
    return abi

@app.route("/")
def home():
    return render_template("Home.html")

@app.route("/exchange")
def exchange():
    senderusername = session.get('username')
    if senderusername==None:
        return render_template("Home.html")
    abi = usdcabi()
    USDC_balance, balance, savingsbalance, loans = scripts.userdata.transactions.userstats(senderusername,abi)
    currency = 'USDC'
    swapto = 'Select a currency'
    return render_template("exchange.html",balance=balance, savingsbalance=savingsbalance,loans=loans,USDC_balance=USDC_balance,currency=currency,swapto=swapto)

@app.route("/signin", methods=['POST', 'GET'])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username)
        print(password)
        verifylogin = scripts.userdata.transactions.verifylogin(
            username, password)
        if verifylogin == True:
            session['username'] = username
            return redirect(url_for('application'))
        else:
            msg = 'Incorrect Username or Password'
            return render_template('Home.html', msg=msg)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form["setusername"]
        password = request.form["setpassword"]
        checkpassword = request.form["confirmpassword"]
        if num_there(password) == True:
            if checkpassword == password:
                if scripts.userdata.transactions.checkexisting(username) == True:
                    if len(password) > 6:
                        special_chars = ['$', '&', '!', '"', '#', '£', '%', "'",
                                         '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '>', '=', '@', '?', '{', '}', '[', ']', '\,', '|', '~', '_']
                        print(special_chars)
                        valid = False
                        for char in password:
                            if char in special_chars:
                                valid = True
                                break
                        if valid == True:
                            session['username'] = username
                            scripts.userdata.transactions.newtransactions(
                                password, username)
                            return redirect(url_for('application'))
                        else:
                            msg = 'Please make sure your password contains a number and a special character.'
                            return render_template('signup.html', msg=msg)
                    else:
                        msg = 'Please make sure your password is at least 6 characters long.'
                        return render_template('signup.html', msg=msg)
                else:
                    msg = 'This email has already signed up for a Doddle account.'
                    return render_template('signup.html', msg=msg)
            else:
                msg = 'Oops! The passwords you entered do not match.'
                return render_template('signup.html', msg=msg)
        else:
            msg = 'Please make sure your password contains a number and a special character.'
            return render_template('signup.html', msg=msg)
    else:
        senderusername = session.get('username')
        print(senderusername)
        return render_template("signup.html")


@app.route("/app", methods=["POST", "GET"])
def application():
    senderusername = session.get('username')
    if senderusername==None:
        return render_template("Home.html")
    abi = usdcabi()
    USDC_balance,balance, savingsbalance, loans = scripts.userdata.transactions.userstats(
        senderusername,abi)
    return render_template("app.html", balance=balance, savingsbalance=savingsbalance, loans=loans)


@app.route("/doddlepay", methods=["POST", "GET"])
def doddlepay():
    senderusername = session.get('username')
    print(senderusername)
    if request.method == "POST":
        recipientemail = request.form["recipient"]
        transferamount = request.form["sendamount"]
        try:
            message = request.form["sendamount"]
        except:
            message = False
        print(recipientemail)
        print(transferamount)
        
        if message!=False:
            scripts.userdata.transactions.sendMessage(recipientemail,message,senderusername)
            
        transactionstatus = scripts.userdata.transactions.doddlePay(recipientemail, senderusername, transferamount)
        
        if transactionstatus == 'nouser':
            msg = 'nouser'
        elif transactionstatus == 'insufficientfunds':
            msg = 'insufficientfunds'
        elif transactionstatus == 'transactionfail':
            msg = 'transactionfail'
        else:
            msg = 'success'
            
        return jsonify(msg)
    return render_template("app.html")


@app.route("/doddlelend", methods=["POST", "GET"])
def doddlelend():
    senderusername = session.get('username')
    print(senderusername)
    if request.method == "POST":
        lendamount = request.form["lendamount"]
        print(lendamount)
        contractabi = usdcabi()
        transactionstatus = scripts.userdata.transactions.doddleLend(
            senderusername, lendamount,contractabi)

        if transactionstatus == 'insufficientfunds':
            msg = 'insufficientfunds'
        elif transactionstatus == 'transactionfail':
            msg = 'transactionfail'
        else:
            msg = 'success'
    return jsonify(msg)


@app.route("/maxtoken", methods=["POST", "GET"])
def maxtoken():
    print('in max token')
    senderusername = session.get('username')
    if senderusername==None:
        return render_template("Home.html")
    if request.method == 'POST':
        currency = request.form["currency"]
        #add function to get abi for currency
        abi = None                                   # add function here to send abi for users token
        balance = scripts.userdata.transactions.checktokenbalance(senderusername,abi)
    return jsonify(balance)

@app.route("/checkbalance", methods=["POST", "GET"])
def checkbalance():
    senderusername = session.get('username')
    if senderusername==None:
        return render_template("Home.html")
    if request.method == 'POST':
        currency = request.form["currency"]
        #add function to get abi for currency
        abi = None                                   # add function here to send abi for users token
        balance = scripts.userdata.transactions.checktokenbalance(senderusername,abi)
    return jsonify(balance)
                
@app.route("/swapto", methods=["POST", "GET"])
def swapto():
    swapfrom = session.get('swapfrom')
    if swapfrom ==None:
        swapfrom = 'USDC'
    if request.method == 'POST':
        tokens = ['Bitcoin','Ethereum','Chainlink','Sushiswap','Olympus Dao','Dopex']
        tokenid = ['BTC','ETH','LINK','SUSHI','OHM','DPX']
        for i in range(len(tokens)):
            if request.form['currency'] == tokens[i]:
                swapto = tokenid[i]
                session['swapto'] = swapto
                selectatoken = ' '
                return render_template("exchange.html",swapto=swapto,currency=swapfrom,selectatoken=selectatoken)
            elif request.form['currency'] == 'ethereum':
                return render_template("home.html")
            else:
                pass # unknown
            
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'Deposit',
        },
        'unit_amount': 2000,
      },
      'quantity': 1,
    }],
    mode='payment',
    success_url='http://localhost:5000/success.html',
    cancel_url='http://localhost:5000/cancel.html',

  )

  return redirect(session.url, code=303)


