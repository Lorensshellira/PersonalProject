import csv
from io import BytesIO, StringIO
from tkinter import Canvas
from reportlab.pdfgen import canvas
from flask_app import app
from flask import make_response, render_template, redirect, flash, session, request
from flask_bcrypt import Bcrypt

from flask_app.models.student import Student
from flask_app.models.admin import Admin
from flask_app.models.teacher import Teacher
from flask_app.models.teacher import Teacher
from flask_app.models.classe import Classe
from flask_app.models.lesson import Lesson

bcrypt = Bcrypt(app)




@app.route('/login/admin', methods = ['POST'])
def loginAdmin():
    if 'user_id' in session:
        return redirect('/')
    if not Admin.validate_user(request.form):
        return redirect(request.referrer)
    user = Admin.get_admin_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/admin')


@app.route('/loginPage/admin')
def loginPageAdmin():
    if 'user_id' in session:
        return redirect('/')
    return render_template('adminLogin.html')

@app.route('/admin')
def adminPage():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Admin.get_admin_by_id(data)
    registredteachers=Teacher.count_teacher()
    registredstudents=Student.count_students()
    registredlessons=Lesson.count_lesson()
    registredclasse=Classe.count_clases()
    if user and user['role'] == 'admin':
        return render_template('dashboardAdmin.html', loggedUser = user , teachers = Teacher.get_all(),students=Student.get_all_student(),classes=Classe.get_all_classes(),lessons=Lesson.get_all_lessons(),registredteachers=registredteachers
                               ,registredstudents=registredstudents,registredclasse=registredclasse,registredlessons=registredlessons)
    return redirect('/logout')

@app.route('/trainer/new')
def newTrainer():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Admin.get_admin_by_id(data)
    if user and user['role'] == 'admin':
        return render_template('registerTrainerr.html')
    return redirect('/logout')
    



@app.route('/register/trainer', methods = ['POST'])
def registerTrainer():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Teacher.validate_userRegister(request.form):
            return redirect(request.referrer)
        user = Teacher.get_teacher_by_email(request.form)
        if user:
            flash('This account already exists', 'emailRegister')
            return redirect(request.referrer)
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']),
            'phone': request.form['phone'],
            'speciality': request.form['speciality']
        }
        Teacher.create(data)
        flash('Trajneri krijuar me sukses', 'succesRegister')
        return redirect(request.referrer)
    return redirect('/')

@app.route('/class/new')
def newClass():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Admin.get_admin_by_id(data)
    if user and user['role'] == 'admin':
        return render_template('registerClass.html')
    return redirect('/logout')

@app.route('/register/class', methods = ['POST'])
def registerClass():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        user = Classe.get_classe_by_id(request.form)
        if user:
            flash('This account already exists', 'emailRegister')
            return redirect(request.referrer)
        data = {
            'className': request.form['className'],
            'schedule': request.form['schedule'],
            'capacity': request.form['capacity'],
            'startDate': request.form['startDate'],
            'endDate': request.form['endDate'],
            'teacher_id': session['user_id']
        }
        Classe.create_class(data)
        flash('klasa e krijuar me sukses', 'succesRegister')
        return redirect(request.referrer)
    return redirect('/')

@app.route ('/shkarkoMesues')
def shkarkoMesues():
    users = Teacher.get_all()
    # Create a string buffer to hold the CSV data
    output = StringIO()
    # Create a CSV writer object
    writer = csv.writer(output)
    # Write the CSV header
    writer.writerow(['email'])
    # Write each user's data to the CSV file
    for user in users:
        writer.writerow([user['email']])
    # Create a Flask response object with the CSV data
    response = make_response(output.getvalue())
    # Set the content type of the response to CSV
    response.headers['Content-Type'] = 'text/csv'
    # Set the content disposition to attachment and set the filename
    response.headers['Content-Disposition'] = 'attachment; filename=membersList.csv'
    return response
@app.route('/shkarkoMesuesPdf')
def download_pdf():
    users = Teacher.get_all()

    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()

    # Create a PDF document
    pdf = canvas.Canvas(buffer)

    # Set the font for better formatting
    pdf.setFont("Helvetica", 12)

    # Add content to the PDF
    pdf.drawString(100, 800, "List of Teachers:")
    y_position = 780  # Starting y position for the first user

    for user in users:
        y_position -= 20  # Adjust the vertical spacing

        # Display user information (replace with your actual data)
        user_info = f"Name: {user['firstName']}, Email: {user['email']}, Role: {user['lastName']}"
        pdf.drawString(100, y_position, user_info)

    # Save the PDF to the buffer
    pdf.save()

    # Move the buffer's cursor to the beginning
    buffer.seek(0)

    # Create a Flask response object with the PDF data
    response = make_response(buffer.read())

    # Set the content type of the response to PDF
    response.headers['Content-Type'] = 'application/pdf'

    # Set the content disposition to inline, so the browser will open the PDF
    response.headers['Content-Disposition'] = 'inline; filename=teachersList.pdf'

    return response
