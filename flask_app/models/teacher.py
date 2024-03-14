from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

PASWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


class Teacher:
    db_name = "myschooldb"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def get_all(cls):
        query = "SELECT * FROM teachers;"
        results = connectToMySQL(cls.db_name).query_db(query)
        teachers = []
        if results:
            for row in results:
                teachers.append(row)
        return teachers

    @classmethod
    def get_teacher_by_email(cls, data):
        query = 'SELECT * FROM teachers where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def get_teacher_by_id(cls, data):
        query = 'SELECT * FROM teachers where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
        
    
    @classmethod
    def create(cls, data):
        query = "INSERT INTO teachers (firstName, lastName, email, password, phone, speciality) VALUES (%(firstName)s, %(lastName)s, %(email)s, %(password)s, %(phone)s, %(speciality)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM teachers where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def count_teacher(cls):
        query = 'SELECT COUNT(*) FROM teachers;'
        results = connectToMySQL(cls.db_name).query_db(query)
        return results[0]['COUNT(*)']
    @classmethod
    def update_profile_pic_teacher(cls, data):
        query = "UPDATE teachers SET profile_pic = %(image)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    @classmethod
    def get_all_appointments(cls):
        query = 'SELECT * FROM appointments;'
        results = connectToMySQL(cls.db_name).query_db(query)
        appointments= []
        if results:
            for appointment in results:
                appointments.append(appointment)
            return appointments
        return appointments    

    @classmethod
    def get_appointment_by_id(cls, data):
        query = "SELECT * FROM appointments WHERE id = %(appointment_id)s"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False

    @classmethod
    def get_appointments_by_vet(cls, data):
        query = "SELECT * FROM appointments LEFT JOIN users ON appointments.user_id = users.id WHERE vet_id = %(vet_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        appointments = []
        if results:
            for appointment in results:
                appointments.append(appointment)
            return appointments
        return appointments
    
    @classmethod 
    def get_appointment_details(cls, data):
        query = "SELECT appointments.*, users.first_name AS user_first_name, users.last_name AS user_last_name, users.email AS user_email FROM appointments LEFT JOIN users ON appointments.user_id = users.id WHERE appointments.id = %(appointment_id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        if results:
            return results[0]
        return False
    
    @classmethod
    def update_accept(cls, data):
        query = "UPDATE appointments SET accepted = 1 WHERE id = %(appointment_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def decline_accept(cls, data):
        query = "UPDATE appointments SET accepted = 2 WHERE id = %(appointment_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    


    @staticmethod
    def validate_user(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailLogin')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordLogin')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_userRegister(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailRegister')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordRegister')
            is_valid = False
        if len(user['firstName'])<1:
            flash("First name is required!", 'nameRegister')
            is_valid = False
        if len(user['lastName'])<1:
            flash("Last name is required!", 'lastNameRegister')
            is_valid = False
        if len(user['speciality'])<1:
            flash("Speciality is required!", 'specialityRegister')
            is_valid = False
        if not user['phone']:
            flash("Last name is required!", 'phoneRegister')
            is_valid = False
        return is_valid
    