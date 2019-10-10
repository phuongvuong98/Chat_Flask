from quart import (Quart, abort, jsonify, make_push_promise, render_template,
                   request, url_for, websocket, Response, session)
from quart_cors import cors, route_cors, websocket_cors

from db import db
import json

from functools import wraps
import uuid

import asyncio


app = Quart(__name__)
# create a Socket.IO server


@app.route('/')
async def index():
    await make_push_promise(url_for('static', filename='http2.css'))
    await make_push_promise(url_for('static', filename='http2.js'))
    return await render_template('index.html')


connected = set()
users = dict()


def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected
        global users
        connected.add(websocket._get_current_object())
        users[id(websocket._get_current_object())
              ] = websocket._get_current_object()
        try:
            return await func(*args, **kwargs)
        finally:
            connected.remove(websocket._get_current_object())
            if id(websocket._get_current_object()) in users:
                del users[id(websocket._get_current_object())]
    return wrapper


@app.websocket('/ws')
# @collect_websocket
@websocket_cors(allow_origin='*')
async def ws():
    global users
    g_user = ""
    try:
        while True:
            data = await websocket.receive()
            print("********")
            # print(type(data))
            # print(json.dumps(data))

            try:
                message_json = json.loads(data)
            except Exception as e:
                print(e)
                print("aa")

            if message_json.get("type") == None:
                await websocket.send("Invalid")
            else:
                if message_json["type"] == "init":
                    g_user = message_json["username"]
                    print(g_user)
                    users[g_user] = websocket._get_current_object()

                if message_json["type"] == "chat":
                    receiver_websocket = users[message_json['receiver']]
                    await receiver_websocket.send(message_json['content'])
                    database = db.Database()

                    database.add_message(
                        message_json['sender'], message_json['receiver'], message_json['content'])
            database = db.Database()
            database.update_websocket_id(
                data, id(websocket._get_current_object()))

            print(users)
    except asyncio.CancelledError:
        del users[g_user]


# @app.websocket('/submit')
# @websocket_cors(allow_origin='*')
# async def sending():
#     global users
#     while True:
#         data = await websocket.receive()
#         message_json = json.loads(data)

#         print(message_json)
#         receiver_websocket = users[message_json['receiver']]
#         receiver_websocket.send(message_json['content'])

#         database = db.Database()

#         database.add_message(
#             message_json['sender'], message_json['receiver'], message_json['content'])

#         # await websocket.send(f"echo {data}")


@app.route('/signup', methods=['POST'])
@route_cors(allow_origin="*")
async def signup():
    data = await request.get_json()
    username = data['username']
    passwd = data['password']

    database = db.Database()

    result = database.create_user(username, passwd)

    if result == "Success":
        return json.dumps({"status": "success"})
    else:
        return Response(json.dumps({"error": result}), 404)


@app.route('/login', methods=['POST', 'GET'])
@route_cors(allow_origin="*")
async def login():
    data = await request.get_json()
    username = data['username']
    passwd = data['password']

    try:
        database = db.Database()
    except Exception as e:
        print(e)

    result = database.check_valid_cred(username, passwd)

    if result == "Success":
        return json.dumps({"status": "success"})
    else:
        return Response(json.dumps({"error": result}), 404)


@app.route('/users', methods=['GET'])
@route_cors(allow_origin="*")
async def list_user():
    data = await request.get_json()
    # print(request.headers['Auth'])

    cred = request.headers['Authorization']

    if cred == None:
        return Response(json.dumps({"error": "Forbidden"}), 403)

    database = db.Database()

    result = database.list_user()

    return {"data": result}


@app.route('/conversation', methods=['GET'])
@route_cors(allow_origin="*")
async def get_conversation():
    data = await request.get_json()
    receiver = request.args.get('username')

    cred = request.headers['Authorization']

    if cred == None or len(cred.split("&")) != 2:
        print("a")
        return Response(json.dumps({"error": "Forbidden"}), 403)

    try:
        database = db.Database()
    except Exception as e:
        print("***********************")
        print(e)

    username = cred.split("&")[0]
    password = cred.split("&")[1]
    isValidUser = database.check_valid_cred(username, password)

    if isValidUser != "Success":
        return Response(json.dumps({"error": "Forbidden"}), 403)

    result = database.show_conversation(username, receiver)

    return json.dumps({"data": result})


@app.route('/chat', methods=['POST'])
@route_cors(allow_origin="*")
async def send_message():
    data = await request.get_json()

    cred = request.headers['Authorization']

    if cred == None or len(cred.split("&")) != 2:
        print("a")
        return Response(json.dumps({"error": "Forbidden"}), 403)

    try:
        database = db.Database()
    except Exception as e:
        print("***********************")
        print(e)

    username = cred.split("&")[0]
    password = cred.split("&")[1]
    isValidUser = database.check_valid_cred(username, password)

    if isValidUser != "Success":
        return Response(json.dumps({"error": "Forbidden"}), 403)

    receiver = data['receiver']
    content = data['content']

    result = database.add_message("luan", receiver, content)

    if result == "Success":
        return json.dumps({"status": "success"})

    return Response(json.dumps({"error": result}), 500)


@app.cli.command('run')
def run():
    app.run(port=5000, certfile='cert.pem', keyfile='key.pem')
