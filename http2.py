import asyncio
import json
import uuid
from functools import wraps

from quart import (Quart, Response, abort, jsonify, make_push_promise,
                   render_template, request, session, url_for, websocket)
from quart_cors import cors, route_cors, websocket_cors

from db import db

app = Quart(__name__)


@app.route('/')
async def index():
    await make_push_promise(url_for('static', filename='http2.css'))
    await make_push_promise(url_for('static', filename='http2.js'))
    return await render_template('index.html')


users = dict()


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if request.headers.get('Authorization') == None:
            return Response(json.dumps({"error": "Bad request"}), 400)

        cred = request.headers['Authorization']

        if cred == None or len(cred.split("&")) != 2:
            return Response(json.dumps({"error": "Forbidden"}), 403)

        database = db.Database()

        username, password = cred.split("&")
        isValidUser = database.check_valid_cred(username, password)

        if isValidUser != "Success":
            return Response(json.dumps({"error": "Forbidden"}), 403)

    return wrapper


@app.websocket('/ws')
@websocket_cors(allow_origin='*')
async def ws():
    global users
    g_user = ""
    try:
        while True:
            data = await websocket.receive()

            try:
                message_json = json.loads(data)
            except Exception as e:
                print(e)

            database = db.Database()

            if message_json.get("type") == None:
                await websocket.send("Invalid")
            else:
                if message_json["type"] == "init":
                    g_user = message_json["username"]
                    users[g_user] = websocket._get_current_object()

                if message_json["type"] == "chat":
                    if users.get(message_json['receiver']) != None:
                        receiver_websocket = users[message_json['receiver']]
                        await receiver_websocket.send(data)

                    database.add_message(
                        message_json['sender'], message_json['receiver'], message_json['content'])
            database.update_websocket_id(
                data, id(websocket._get_current_object()))

    except asyncio.CancelledError:
        del users[g_user]


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
@auth_required
@route_cors(allow_origin="*")
async def list_user():
    data = await request.get_json()

    try:
        database = db.Database()
    except Exception as e:
        print(e)

    result = database.list_user()

    return {"data": result}


@app.route('/conversation', methods=['GET'])
@auth_required
@route_cors(allow_origin="*")
async def get_conversation():
    data = await request.get_json()

    receiver = request.args.get('username')
    username = request.headers['Authorization'].split("&")[0]

    try:
        database = db.Database()
    except Exception as e:
        print(e)

    result = database.show_conversation(username, receiver)

    return json.dumps({"data": result})


@app.route('/chat', methods=['POST'])
@auth_required
@route_cors(allow_origin="*")
async def send_message():
    data = await request.get_json()

    username = request.headers['Authorization'].split("&")[0]
    receiver = data['receiver']
    content = data['content']

    try:
        database = db.Database()
    except Exception as e:
        print(e)

    result = database.add_message(username, receiver, content)

    if result == "Success":
        return json.dumps({"status": "success"})

    return Response(json.dumps({"error": result}), 500)


@app.cli.command('run')
def run():
    app.run(port=5000, certfile='cert.pem', keyfile='key.pem')
