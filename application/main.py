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


import fcntl
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import config
import socket
import struct

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app, async_mode=async_mode)


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

data = {
  "local_ip": get_ip_address('eth0'),
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


@socketio.on('ping')
def pong():
    emit('pong')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)




