from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash  

class Lesson:
    db_name = 'myschooldb'
    def __init__(self , data):
        self.id = data['id']
        self.lenda = data['lenda']
        self.klasa = data['klasa']
        self.kapitulli = data['kapitulli']
        self.tema = data['tema']
        self.objektivi = data['objektivi']
        self.lidhja_me_fushat = data['lidhja_me_fushat']
        self.situata_e_te_nxenit = data['situata_e_te_nxenit']
        self.fjalet_kyce = data['fjalet_kyce']
        self.pershkrimi = data['pershkrimi']
        self.motivimi = data['motivimi']
        self.post_post_file = data['post_post_file']
        self.link_file = data['link_file']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def create_lesson(cls, data):
        query = "INSERT INTO lessons (lenda, klasa, kapitulli, tema,objektivi, pershkrimi,lidhja_me_fushat,situata_e_te_nxenit,fjalet_kyce,motivimi, post_post_file, link_file,  teacher_id) VALUES ( %(lenda)s, %(klasa)s, %(kapitulli)s, %(tema)s, %(objektivi)s,%(pershkrimi)s, %(lidhja_me_fushat)s, %(situata_e_te_nxenit)s, %(fjalet_kyce)s, %(motivimi)s, %(post_post_file)s, %(link_file)s, %(teacher_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)   
    
    @classmethod
    def update(cls, data):
        query = "UPDATE lessons set description = %(description)s, address=%(address)s, education_experience = %(education_experience)s,city = %(city)s,experience = %(experience)s,employment_status = %(employment_status)s WHERE jobs.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)   
        
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM lessons WHERE id = %(lesson_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def count_lesson(cls):
        query = 'SELECT COUNT(*) FROM lessons;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    
    @classmethod
    def get_lessons_by_id(cls, data):
        query = 'SELECT * FROM lessons WHERE id= %(lesson_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    @classmethod
    def get_all_lessons(cls):
        query = 'SELECT * FROM lessons;'
        results = connectToMySQL(cls.db_name).query_db(query)
        lessons = []
        if results:
            for lesson in results:
                lesson = Lesson(lesson)
                lessons.append(lesson)
            return lessons
        return lessons
    @classmethod
    def update_star_rating(cls, job_id, rating):
        query = "UPDATE jobs SET star_rating = %(rating)s WHERE id = %(job_id)s;"
        data = {
            'job_id': job_id,
            'rating': rating
        }
        connectToMySQL(cls.db_name).query_db(query, data) 
    @classmethod
    def delete_all_job_ratings(cls, data):
        query ="DELETE FROM ratings where ratings.job_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def search(cls, search_query):

        query = f"""
            SELECT * FROM jobs where jobs.title LIKE '{search_query}%'
        """

        try:
            results = connectToMySQL(cls.db_name).query_db(query)

            jobs = []
            if results:
                for job in results:
                    jobs.append(job)
            return jobs
        except Exception as e:
            print("An error occurred:", str(e))
            return []
    @classmethod
    def createPayment(cls,data):
        query = "INSERT INTO payments (ammount, status, job_id) VALUES (%(ammount)s, %(status)s, %(job_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_allUserPayments(cls, data):
        query = "SELECT * FROM payments where costumer_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        payments = []
        if results:
            for pay in results:
                payments.append(pay)
        return payments    
    
    @classmethod
    def get_teacher_lessons_by_id(cls, data):
        query = 'SELECT * FROM lessons WHERE teacher_id= %(teacher_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        return results 
    
    @classmethod
    def get_lesson_creator(cls, data):
        query="SELECT lessons.id AS lesson_id, lessons.teacher_id, teachers.id AS teacher_id, teacher.firstName as firstName, teachers.lastName as lastName, email FROM lessons LEFT JOIN teachers ON lessons.teacher_id = teachers.id WHERE lessons.id= %(lesson_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
   
    @staticmethod
    def validateImage(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'job_post_image')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validateImageLogo(data):
        is_valid = True
        if len(data) < 1:
            flash('Please select at least one image', 'company_logo')
            is_valid = False 
        return is_valid
    
    @staticmethod
    def validate_job(provider):
        is_valid = True
        if len(provider['title'])< 3:
            flash('Title must be more than 2 characters', 'title')
            is_valid = False
        if len(provider['description'])< 3:
            flash('Description must be more than 2 characters', 'description')
            is_valid = False
        if  len(provider['address'])< 3:
            flash('Salary must be more or equal to 8 characters', 'address')
            is_valid = False
        if len(provider['education_experience'])< 4:
            flash('Education and Experience must be more or equal to 4 characters', 'education_experience')
            is_valid = False
        if len(provider['city'])< 4:
            flash('Benefits must be more or equal to 4 characters', 'city')
            is_valid = False
        if not (provider['employement_status']):
            flash('Choose Employement status', 'employement_status')
            is_valid = False
        if len(provider['experience'])> 3:
            flash(' Enter a valid experience', 'experience')
            is_valid = False
        return is_valid
    