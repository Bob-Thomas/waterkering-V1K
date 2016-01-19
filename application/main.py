# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
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


from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import config
import socket
import struct
import time
import threading
app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app, async_mode=async_mode)


def get_ip_address():
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

data = {
  "local_ip": get_ip_address(),
  "timestamp": 234189073,
  "station": 0,
  "sensors": [
    {
      "name": "water_pressure",
      "value": 0.0
    },
    {
      "name": "whateversenseor",
      "value": 0.0
    }
  ],
  "warning_level": "orange",
  "doors_open": False,
  "doors_opening": False
}


@app.route('/')
def home():
    return render_template('home.html', data=data)

direction = 0
def test():
    global direction
    threading.Timer(0.10, test).start()
    value = data['sensors'][0]['value']
    if value >= 100:
        direction = 1
    elif value <= 0:
        direction = 0
    if direction == 0 :
        value = value+1
    elif direction == 1:
        value = value-1

    data['sensors'][0]['value'] = value
    if value >= 100:
        data['warning_level'] = 'blue'
    elif value < 50:
        data['warning_level'] = 'lightGreen'
    elif value > 50 and value < 75:
        data['warning_level'] = 'orange'
    elif value >= 75:
        data['warning_level'] = 'red'

    socketio.emit('update', {'data':data})


test()


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
