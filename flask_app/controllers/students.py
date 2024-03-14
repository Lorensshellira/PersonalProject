import csv
from io import StringIO
import math
import random
from flask_app import app
from flask import make_response, render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from .env import ADMINEMAIL, UPLOAD_FOLDER
from .env import PASSWORD
from flask_app.models.student import Student
from flask_app.models.teacher import Teacher
from flask_app.models.classe import Classe
bcrypt = Bcrypt(app)

import paypalrestsdk
from .env import ALLOWED_EXTENSIONS

from datetime import datetime
from urllib.parse import unquote


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


import os
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import HTTPException, NotFound
import urllib.parse

import smtplib


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginPage')
def loginPage():
    if 'user_id' in session:
        return redirect('/dashboardstudent')
    return render_template('loginstudent.html')


@app.route('/')
def indexstudent():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Student.get_student_by_id(data)
        if user['isVerified'] == 0:
            return redirect('/verify/account')
        return redirect('/dashboardstudent')
    return redirect('/logout')

@app.route('/verify/account')
def verifyAccount():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Student.get_student_by_id(data)
        if user['isVerified'] == 0:
            return render_template('verifyAccount.html')
        
    return redirect('/')

@app.route('/verify/account', methods = ['POST'])
def confirmAccountVerification():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Student.get_student_by_id(data)
        if user['verificationCode'] != request.form['verificationCode']:
            flash('Incorrect verification code', 'verificationCode')
            return redirect(request.referrer)
        Student.approve(data)
    return redirect('/dashboardstudent')




@app.route('/register')
def registerPage():
    if 'user_id' in session:
        return redirect('/dashboardstudent')
    return render_template('registerstudent.html')


@app.route('/register', methods = ['POST'])
def registerStudent():
    if 'user_id' in session:
        return redirect('/')
    if not Student.validate_userRegister(request.form):
        return redirect(request.referrer)
    user = Student.get_student_by_email(request.form)
    if user:
        flash('This account already exists', 'emailRegister')
        return redirect(request.referrer)
    

    string = '0123456789ABCDEFGHIJKELNOPKQSTUV'
    vCode = ""
    length = len(string)
    for i in range(8) :
        vCode += string[math.floor(random.random() * length)]
    verificationCode = vCode

    # line- i know for sure that my validate_user was true. User had all the required info
    data = {
        'firstName': request.form['firstName'],
        'lastName': request.form['lastName'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verificationCode': verificationCode
    }
    session['user_id'] = Student.create(data)

    LOGIN = ADMINEMAIL
    TOADDRS  = request.form['email']
    SENDER = ADMINEMAIL
    SUBJECT = 'Verify Your Account'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
        % ((SENDER), "".join(TOADDRS), SUBJECT) )
    msg += f'Use this verification code to activate your account: {verificationCode}'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()

    
    return redirect('/verify/account')



@app.route('/login/student', methods = ['POST'])
def loginStudent():
    if 'user_id' in session:
        return redirect('/')
    if not Student.validate_user(request.form):
        return redirect(request.referrer)
    user = Student.get_student_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/dashboardstudent')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Student.get_student_by_id(data)
    if user['isVerified'] == 0:
        return redirect('/verify/account')
    return render_template('profile.html', loggedUser = user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

UPLOAD_FOLDER = 'flask_app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/profilepic/student', methods=['POST'])
def new_profil_pic_student():
    if 'user_id' not in session:
        return redirect('/loginpage')
    data = {"id": session['user_id']}
    
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['image'] = filename
            Student.update_profile_pic_student(data)
    return redirect('/dashboardstudent')

@app.route('/dashboardstudent')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Student.get_student_by_id(data)
    registredteachers=Teacher.count_teacher()
    registredstudents=Student.count_students()
    registredclasses=Classe.count_clases()
    
    return render_template('dashboardstudent.html',user=user, loggedUser = Student.get_student_by_id(data), pagesat = Student.get_allUserPayments(data), teachers = Teacher.get_all(),students=Student.get_all_student(),classes=Classe.get_all_classes(),registredteachers=registredteachers
                               ,registredstudents=registredstudents,registredclasses=registredclasses)



@app.route('/checkout/paypal')
def checkoutPaypal():
    if 'user_id' not in session:
            return redirect('/')
    cmimi = 100
    ora = 2
    targa = 'AA123AA'
    totalPrice = round(cmimi * ora)

    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AYckYn5asNG7rR9A2gycCw-N2Du3GXH4ytNfU5ueLeYKaUwjKFL-aZMu3owCwfs_D1fydp2W-HSVieZ0",
            "client_secret": "EJu8H94UNn6b2Xigp26rf1pIs6NW-WrweGw-RkboWLUjWfHK2m46qrFObh_rL_HPSwvfipNyFoYdoa3K"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": totalPrice,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Pagese per parkim per makinen me targe {targa} per {ora} orë!"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, totalPrice=totalPrice),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)






@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AYckYn5asNG7rR9A2gycCw-N2Du3GXH4ytNfU5ueLeYKaUwjKFL-aZMu3owCwfs_D1fydp2W-HSVieZ0",
            "client_secret": "EJu8H94UNn6b2Xigp26rf1pIs6NW-WrweGw-RkboWLUjWfHK2m46qrFObh_rL_HPSwvfipNyFoYdoa3K"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('totalPrice')
            status = 'Paid'
            member_id = session['user_id']
            data = {
                'ammount': ammount,
                'status': status,
                'member_id': member_id
            }
            Student.createPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/dashboard')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/dashboard')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/dashboard')

@app.route('/student/<int:id>')
def viewstudent(id):
    if 'user_id' in session:
        data = {
            'user_id': session.get('user_id'),
            'id': id
        }
        loggedUser = Student.get_student_by_id(data)
        teacher = Teacher.get_teacher_by_id(data)
        student = Student.get_student_by_id(data)
        return render_template('studentdetails.html', loggedUser=loggedUser, teacher=teacher,student=student)

    else:
        return redirect('/')
