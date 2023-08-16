from flask import Flask, request, Response, render_template
import subprocess
import psutil
import requests
import time
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def homepage():
    ip = subprocess.Popen('ifconfig | grep "inet " | awk "{print \$2}" | sed "s|127.0.0.1||g" | sed "s|localhost||g" ', shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    hostname = subprocess.Popen(' hostname ', shell=True, stdout=subprocess.PIPE).stdout.read().strip()

    index_html = f"""
    <head>
    <title>Clendy Server</title>
    </head>
    <body>
        <h1>Hello Clendy</h1>
        <br>
        <form action="/stress" method="GET">
            <label for="timeout">timeout:</label>
            <input type="text" id="timeout" name="timeout" required>
            <br>
            <label for="units">units:</label>
            <input type="radio" id="units" name="unit" value="s" checked>seconds
            <input type="radio" id="units" name="unit" value="m">minutes
            <br>
            <input type="submit" value="STRESS!!">
        </form>
        <br>
        <h3>Server Info</h3>
        <table border="1">
            <th>IP</th>
            <th>HOSTNAME</th>
            <tr>
                <td align="center">{ip.decode('ascii')}</td>
                <td align="center">{hostname.decode('ascii')}</td>
            </tr>
        </table>
    </body>
    """
    return index_html

def stress_cpu(timeout, unit):
    stress = subprocess.Popen(f"stress -c 2 --timeout {timeout}{unit}", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    print(stress)
    return stress

@app.route('/stress')
def stress_endpoint():
    timeout = int(request.args.get('timeout', 60))
    unit = request.args.get('unit', 's')

    if timeout > 300 and unit == "s":
        return Response("Sorry, Only supported under 300s", status=403)
    elif timeout >= 5 and unit == "m":
        return Response("Sorry, Only supported under 5m", status=403)
    elif unit not in ['s', 'm']:
        return Response("The units entered are unsupported units. (Only Support \"s\"(seconds), \"m\"(minutes))", status=403)

    process = multiprocessing.Process(target=stress_cpu, args=(timeout, unit))
    process.start()

    return f"Stress initiated for {timeout} {unit}"

@app.route('/healthz')
def healthz():
    return {"msg": "Healthy"}

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5050")
