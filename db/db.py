import json
import pprint
import re
import ssl

import bcrypt
import pymongo


class Database:
    def __init__(self):
        connection = pymongo.MongoClient(
            "mongodb+srv://3man:Admin123@c0-xeenv.mongodb.net/admin?retryWrites=true&w=majority", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)

        # creating database
        db = connection.chat

        # creating document
        self.user = db.user
        self.message = db.message

    def create_user(self, username, passwd):
        if re.match("^[a-zA-Z0-9_.]+$", username) == False:
            return "Invalid username"

        if re.match("^[a-zA-Z0-9_. ]+$", passwd) == False:
            return "Invalid password"

        if self.user.count_documents({'username': username}, limit=1) != 0:
            return "user already exists"

        user = {
            "username": username,
            "passwd": get_hashed_password(passwd.encode('utf-8')),
        }

        # inserting new user
        result = self.user.insert_one(user)

        if result.inserted_id == None:
            return "Error has occurred"

        return "Success"

    def check_valid_cred(self, username, passwd):
        if re.match("^[a-zA-Z0-9_.]+$", username) == False:
            return "Invalid username"

        if re.match("^[a-zA-Z0-9_. ]+$", passwd) == False:
            return "Invalid password"

        user = self.user.find_one({
            "username": username,
        })

        if user == None:
            return "Error has occurred"

        if check_password(passwd.encode('utf-8'), user['passwd']):
            return "Success"

        return "Error has occurred"


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt(12))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)
