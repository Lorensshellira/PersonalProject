
from flask_app import app

from flask import render_template, redirect, session, request, flash,url_for
import os

from werkzeug.utils import secure_filename

from flask_app.models.student import Student
from flask_app.models.teacher import Teacher
from flask_app.models.lesson import Lesson
from flask_app.models.classe import Classe

from .env import UPLOAD_FOLDER 

from .env import ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from datetime import datetime
import paypalrestsdk


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/lesson')
def lesson_index():
    return render_template('results.html')


@app.route('/postalesson')
def postalessonn():
    if 'user_id' not in session:
        return redirect('/')
    loggedUserData= {
        'user_id': session['user_id']
    }
    return render_template('addlessons.html',loggedUser = Teacher.get_teacher_by_id(loggedUserData))


@app.route('/createlesson', methods=['GET', 'POST'])
def create_lesson():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'post_post_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['post_post_file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename
            filename = time
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
   
            data = {
                'lenda': request.form['lenda'],
                'klasa': request.form['klasa'],
                'kapitulli': request.form['kapitulli'],
                'tema': request.form['tema'],
                'objektivi': request.form['objektivi'],
                'lidhja_me_fushat': request.form['lidhja_me_fushat'],
                'situata_e_te_nxenit': request.form['situata_e_te_nxenit'],
                'fjalet_kyce': request.form['fjalet_kyce'],
                'pershkrimi': request.form['pershkrimi'],
                'motivimi': request.form['motivimi'],
                'link_file': request.form['link_file'],
                'post_post_file': filename,
                'teacher_id': session['user_id']
            }

    
            Lesson.create_lesson(data)
            return redirect(request.referrer)
        
    return redirect('/dashboardteacher')


    
@app.route('/all_lessons')
def view_all_lessons():
    lessons = Lesson.get_all_lessons()
    loggedUserData = {
        'user_id': session['user_id']
    }
    
    return render_template('viewlessons.html', lessons=lessons,loggedUser = Teacher.get_teacher_by_id(loggedUserData),classes=Classe.get_all_classes())



@app.route('/lesson/<int:id>')
def viewjob1(id):
    if 'user_id' in session:
        data = {
            'user_id': session.get('user_id'),
            'lesson_id': id
        }
        loggedUser = Teacher.get_teacher_by_id(data)
        lesson = Lesson.get_lessons_by_id(data)
        lessoncreator = Lesson.get_lesson_creator(data)
        return render_template('lessondetail.html', lesson=lesson, loggedUser=loggedUser, lessoncreator=lessoncreator)

    else:
        return redirect('/')
    


@app.route('/job/edit/<int:id>')
def editJob1(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        return render_template('editjob.html', job=job)
    return redirect('/dashboarProvider')


@app.route('/job/update/<int:id>', methods = ['POST'])
def updateJob1(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'provider_id': session.get('provider_id'),
        'job_id': id
    }
    job = Job.get_job_by_id(data)
    if job and job['provider_id'] == session['provider_id']:
        data = {
            'description': request.form['description'],
            'address': request.form['address'],
            'education_experience': request.form['education_experience'],
            'city': request.form['city'],
            'experience': request.form['experience'],
            'employment_status': request.form['employment_status'],
            'id': id
        }
        Job.update(data)
        return redirect('/job/'+ str(id))
    return redirect('/dashboarProvider')



@app.route('/job/delete/<int:id>')
def deleteJob1(id):
    if 'provider_id' not in session:
        return redirect('/')
    data = {
        'job_id': id
    }
    Job.delete(data)
    return redirect(request.referrer)

@app.route('/rate_job/<int:job_id>', methods=['POST'])
def rate_job1(job_id):
    if 'costumer_id' not in session:
        return redirect('/')
    
    if 'provider_id' in session:
        return redirect('/logout')

    rating = int(request.form.get('rating', 0))

    if 1 <= rating <= 5:
        Job.update_star_rating(job_id, rating)
        flash('Rating submitted successfully!', 'success')
    else:
        flash('Invalid rating value. Please choose a value between 1 and 5.', 'error')

    return redirect('/dashboard')

    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/dashboard')

