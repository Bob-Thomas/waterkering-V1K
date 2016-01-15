import fcntl

from flask import Flask, render_template
import config
import socket
import struct

app = Flask(__name__)
app.config.from_object(config)

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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)




