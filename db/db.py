import json
import pprint
import re
import ssl


import bcrypt
import pymongo

from bson.json_util import dumps
from datetime import datetime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
            print("aa")
            connection = pymongo.MongoClient(
                "mongodb+srv://3man:Admin123@c0-xeenv.mongodb.net/admin?retryWrites=true&w=majority", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)

            # creating database
            db = connection.chat

            cls.user = db.user
            cls.message = db.message

        return cls._instances[cls]


class Database(metaclass=Singleton):
    pass
    # def __init__(self):

    #     connection = pymongo.MongoClient(
    #         "mongodb+srv://3man:Admin123@c0-xeenv.mongodb.net/admin?retryWrites=true&w=majority", ssl=True, ssl_cert_reqs=ssl.CERT_NONE)

    #     # creating database
    #     db = connection.chat

    #     # creating document
    #     self.user = db.user
    #     self.message = db.message

    def create_user(self, username, passwd):
        if validate_string(username) == False or validate_string(passwd) == False:
            return "Invalid username or password"

        if self.user.count_documents({'username': username}, limit=1) != 0:
            return "user already exists"

        user = {
            "username": username,
            "passwd": get_hashed_password(passwd.encode('utf-8')),
        }

        # inserting new user
        try:
            result = self.user.insert_one(user)
        except pymongo.errors.AutoReconnect:
            print("a")

        if result.inserted_id == None:
            return "Error has occurred"

        return "Success"

    def check_valid_cred(self, username, passwd):
        if validate_string(username) == False or validate_string(passwd) == False:
            return "Invalid username or password"

        try:
            user = self.user.find_one({
                "username": username,
            })
        except pymongo.errors.AutoReconnect:
            print("a")

        if user == None:
            return "Error has occurred"

        if check_password(passwd.encode('utf-8'), user['passwd']):
            return "Success"

        return "Error has occurred"

    def list_user(self):
        return list(self.user.find({}, {"username": 1, "_id": 0}))

    def show_conversation(self, sender, receiver):
        if validate_string(sender) == False or validate_string(receiver) == False:
            return "Error has occurred"

        party = {
            "sender": sender,
            "receiver": receiver,
        }

        try:
            conversation = self.message.find(party, {"_id": 0})
        except:
            print("a")

        return list(conversation)

    def add_message(self, sender, receiver, content):
        conversation = {
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "inserted_at": datetime.utcnow().timestamp(),
        }

        result = self.message.insert_one(conversation)

        if result.inserted_id == None:
            return "Error has occurred"

        return "Success"


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt(12))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


def validate_string(str):
    return re.match("^[a-zA-Z0-9_.]+$", str)
