from quart import (Quart, abort, jsonify, make_push_promise, render_template,
                   request, url_for, websocket, Response)
from quart_cors import cors, route_cors, websocket_cors

from db import db
import json

from functools import wraps
import uuid


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
@collect_websocket
@websocket_cors(allow_origin='*')
async def ws():
    while True:
        print(users)
        data = await websocket.receive()
        await websocket.send(f"echo {data}")


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


@app.route('/login', methods=['POST'])
@route_cors(allow_origin="*")
async def login():
    data = await request.get_json()
    username = data['username']
    passwd = data['password']

    database = db.Database()

    result = database.check_valid_cred(username, passwd)

    if result == "Success":
        return json.dumps({"status": "success"})
    else:
        return Response(json.dumps({"error": result}), 404)


@app.route('/users', methods=['GET'])
@route_cors(allow_origin="*")
async def list_user():
    data = await request.get_json()
    print(request.headers['Host'])

    database = db.Database()

    result = database.list_user()

    return {"data": result}


@app.route('/conversation', methods=['GET'])
@route_cors(allow_origin="*")
async def get_conversation():
    data = await request.get_json()
    print(request.headers['Authorization'])
    # party = data['party']

    database = db.Database()

    result = database.show_conversation("luan", "l1uan")

    return json.dumps({"data": result})


@app.route('/chat', methods=['POST'])
@route_cors(allow_origin="*")
async def send_message():
    data = await request.get_json()
    print(request.headers['Authorization'])
    # party = data['party']

    receiver = data['receiver']
    content = data['content']

    database = db.Database()

    result = database.add_message("luan", receiver, content)

    if result == "Success":
        return json.dumps({"status": "success"})

    return Response(json.dumps({"error": result}), 500)


@app.cli.command('run')
def run():
    app.run(port=5000, certfile='cert.pem', keyfile='key.pem')
