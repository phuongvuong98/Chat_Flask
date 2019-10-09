from quart import (Quart, abort, jsonify, make_push_promise, render_template,
                   request, url_for, websocket, Response)
from quart_cors import cors, route_cors, websocket_cors

from db import db
import json

app = Quart(__name__)


@app.route('/')
async def index():
    await make_push_promise(url_for('static', filename='http2.css'))
    await make_push_promise(url_for('static', filename='http2.js'))
    # return await render_template('index.html')
    return "haha"


@app.websocket("/")
@websocket_cors(allow_origin="127.0.0.1:5000/")
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send(f"echo {data}")


@app.route('/signup', methods=['POST'])
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


@app.cli.command('run')
def run():
    app.run(port=5000, certfile='cert.pem', keyfile='key.pem')
