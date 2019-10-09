import pymongo
import pprint
import ssl
import re
import bcrypt

from db import settings

client = pymongo.MongoClient("mongodb+srv://3man:Admin123@c0-xeenv.mongodb.net/admin?retryWrites=true&w=majority", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
db = client.javatpoint  
employee = {"id": "101",  
"name": "Peter",  
"profession": "Software Engineer",  
}  
# Creating document  
employees = db.employees  
# Inserting data  
employees.insert_one(employee)  
# Fetching data  
pprint.pprint(employees.find_one())

class Database:
    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGODB_DB'], ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
        
        # creating database
        db = connection[settings['MONGODB_DB']]

        # creating document
        self.user = db["user"]
        self.message = db["message"]
    
    def create_user(self, username, password):
        if re.match("^[a-zA-Z0-9_.-]+$", username):
            return "Invalid username"

        if re.match("^[a-zA-Z0-9_.- ]+$", password):
            return "Invalid password"
        
        if self.user.count_documents({ 'username': username }, limit = 1) != 0:
            return "user already exists"
        
        user = {
            "username": username,
            "passwd": get_hashed_password(password),
        }

        # inserting new user
        result = self.user.insert_one(user)




def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt(12))

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)