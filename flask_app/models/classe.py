from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

PASWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
class Classe:
    db_name = 'myschooldb'
    def __init__(self , data):
        self.id = data['id']
        self.className = data['className']
        self.schedule = data['schedule']
        self.capacity = data['capacity']
        self.startDate = data['startDate']
        self.endDate = data['endDate']
       
    @classmethod
    def create_class(cls, data):
        query = "INSERT INTO classes (className, schedule, capacity, startDate, endDate, teacher_id) VALUES ( %(className)s, %(schedule)s, %(capacity)s, %(startDate)s, %(endDate)s, %(teacher_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def update(cls, data):
        query = "UPDATE classes set className = %(className)s, schedule=%(schedule)s, registred = %(registred)s,capacity = %(capacity)s,startDate = %(startDate)s,endDate = %(endDate)s WHERE classes.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)   
        
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM classes WHERE id = %(classes_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def count_clases(cls):
        query = 'SELECT COUNT(*) FROM classes;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    
    @classmethod
    def get_classe_by_id(cls, data):
        query = 'SELECT * FROM classes where id = %(classe_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    @classmethod
    def get_all_classes(cls):
        query = "SELECT * FROM classes;"
        results = connectToMySQL(cls.db_name).query_db(query)
        classes = []
        if results:
            for row in results:
                classes.append(row)
        return classes
   
    
    @classmethod
    def get_provider_jobs_by_id(cls, data):
        query = 'SELECT * FROM jobs WHERE provider_id= %(provider_id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        return results 
    
    @classmethod
    def get_job_creator(cls, data):
        query="SELECT jobs.id AS job_id, jobs.provider_id, providers.id AS provider_id, provider.first_name as first_name, providers.last_name as last_name, profession,email FROM jobs LEFT JOIN providers ON jobs.provider_id = providers.id WHERE jobs.id= %(job_id)s;"
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
    