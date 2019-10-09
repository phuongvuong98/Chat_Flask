from quart import (Quart, abort, jsonify, make_push_promise, render_template,
                   request, url_for, websocket)
from quart_cors import cors, route_cors, websocket_cors

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
async def calculate():
    data = await request.get_json()
    operator = data['operator']
    try:
        a = int(data['a'])
        b = int(data['b'])
    except ValueError:
        abort(400)
    if operator == '+':
        return jsonify(a + b)
    elif operator == '-':
        return jsonify(a - b)
    elif operator == '*':
        return jsonify(a * b)
    elif operator == '/':
        return jsonify(a / b)
    else:
        abort(400)


@app.cli.command('run')
def run():
    app.run(port=5000, certfile='cert.pem', keyfile='key.pem')
