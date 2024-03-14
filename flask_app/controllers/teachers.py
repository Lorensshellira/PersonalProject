from flask_app import app
from flask import render_template, redirect, flash, session, request
from flask_app.models.admin import Admin
from flask_bcrypt import Bcrypt
from .env import ADMINEMAIL
from .env import PASSWORD
from flask_app.models.student import Student
from flask_app.models.teacher import Teacher
from flask_app.models.classe import Classe
import paypalrestsdk
from .env import ALLOWED_EXTENSIONS
from .env import UPLOAD_FOLDER

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

bcrypt = Bcrypt(app)


@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')


@app.route('/loginTeacher')
def loginT():
    if 'user_id' in session:
        return redirect('/dashboardteacher')
    return render_template('loginteacher.html')

@app.route('/login/teacher', methods = ['POST'])
def loginTeacher():
    if 'user_id' in session:
        return redirect('/')
    if not Teacher.validate_user(request.form):
        return redirect(request.referrer)
    user = Teacher.get_teacher_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/dashboardteacher')
@app.route('/dashboardteacher')
def dashboardTeach():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Teacher.get_teacher_by_id(data)
    registredteachers=Teacher.count_teacher()
    registredstudents=Student.count_students()
    registredclasses=Classe.count_clases()
   
    return render_template('dashboardTeacher.html',user=user, loggedUser = Teacher.get_teacher_by_id(data), pagesat = Student.get_allUserPayments(data), teachers = Teacher.get_all(),students=Student.get_all_student(),classes=Classe.get_all_classes(),registredteachers=registredteachers
                               ,registredstudents=registredstudents,registredclasses=registredclasses)


@app.route('/teacher/<int:id>')
def viewteacher(id):
    if 'user_id' in session:
        data = {
            'user_id': session.get('user_id'),
            'id': id
        }
        loggedUser = Student.get_student_by_id(data)
        teacher = Teacher.get_teacher_by_id(data)
        
        return render_template('teacherdetails.html', loggedUser=loggedUser, teacher=teacher)

    else:
        return redirect('/')
@app.route('/postalesson')
def postalesson():
    if 'user_id' not in session:
        return redirect('/')
    loggedUserData = {
        'user_id': session['user_id']
    }
    return render_template('addlessons.html',loggedUser = Teacher.get_teacher_by_id(loggedUserData))

UPLOAD_FOLDER = 'flask_app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/profilepic/teacher', methods=['POST'])
def new_profil_pic_teacher():
    if 'user_id' not in session:
        return redirect('/loginpage')
    data = {"id": session['user_id']}
    
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['image'] = filename
            Teacher.update_profile_pic_teacher(data)
    return redirect('/dashboardteacher')

@app.route('/appointment/<int:appointment_id>', methods=['POST'])
def appointment(appointment_id):
    appointment_details = Vet.get_appointment_details(data={'appointment_id': appointment_id})
    accepeted = appointment_details['accepted']
    email=appointment_details['user_email']

    LOGIN = ADMINEMAIL
    TOADDRS = email
    SENDER = ADMINEMAIL
    SUBJECT = 'INFO ABOUT APPOINTMENT'
    
    if not appointment_details:
        return "Appointment not found", 404

    service = appointment_details['service']
    date = appointment_details['date']
    time = appointment_details['time']
    name=appointment_details['user_first_name']

    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
           % ((SENDER), "".join(TOADDRS), SUBJECT))

    if 'accept' in request.form:
        msg += f"Dear {name},\n\n"
        msg += f"Thank you for choosing our services.\n\nWe are pleased to inform you that your appointment for {service} on {date} at {time} has been accepted. We are looking forward to welcoming you and your pet. If you have any questions or require further assistance, please do not hesitate to contact us.\n\nBest regards,\nPAWFECTION VET CLINIC"
        Vet.update_accept(data={'appointment_id': appointment_id})

    elif 'decline' in request.form:
        msg += f"Dear {name},\n\n"
        msg += f"We regret to inform you that your appointment for {service} on {date} at {time} has been declined by the vet. \n\nWe apologize for any inconvenience this may have caused. If you have any concerns or would like to reschedule, please reach out to us. Thank you for your understanding.\n\nBest regards,\n PAWFECTION VET CLINIC"
        Vet.decline_accept(data={'appointment_id': appointment_id})

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()
    return redirect(request.referrer)