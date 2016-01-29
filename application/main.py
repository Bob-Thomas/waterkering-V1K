# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
import socket
import config

import pyqrcode
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
async_mode = None
if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app, async_mode=async_mode)
amount_users = 0


def get_ip_address():
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

data = {
  "local_ip": get_ip_address(),
  "timestamp": 234189073,
  "station": 0,
  "users": amount_users,
  "sensors": [
    {
      "name": "Water Level",
      "value": 0.0
    }
  ],
  "warning_level": "lightGreen",
  "door_status": 'open',
}


@app.route('/')
def home():
    return render_template('home.html', data=data)


@app.route('/sensor/update', methods=['POST', 'GET'])
def sensor_update():
    global data
    if request.method == 'POST':
        # print request.form.to_dict()['value']
        json_data = request.form.to_dict()
        value = int(json_data['value'])
        door_status = json_data['door_status']
        data['sensors'][0]['value'] = value
        if value < 50:
            data['warning_level'] = 'lightGreen'
        elif 50 < value < 75:
            data['warning_level'] = 'orange'
        elif value >= 75:
            data['warning_level'] = 'red'

        data['door_status'] = door_status
        socketio.emit('update', {'data': data})
        return jsonify(json_data)
    else:
        return 'ok'


@socketio.on('connect', namespace='/')
def test_connect():
    global amount_users, data
    amount_users += 1
    data['users'] = amount_users
    socketio.emit('update', {'data': data})


@socketio.on('disconnect', namespace='/')
def test_disconnect():
    global amount_users, data
    if amount_users > 0:
        amount_users -= 1
        data['users'] = amount_users
        socketio.emit('update', {'data': data})

if __name__ == '__main__':
    port = 5000
    debug = True
    url = pyqrcode.create('http:/'+str(get_ip_address()))
    url.svg('static/images/qr.svg', scale=8)
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
