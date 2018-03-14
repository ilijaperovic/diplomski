import datetime as datetime
import sqlite3
import sys
import paho.mqtt.client as mqtt
import time

import requests
from flask import Flask, render_template, g, json
from requests import RequestException

app = Flask(__name__)
app.database = "C:/Users/Ilija/PycharmProjects/diplomski/diplomski.sqlite"

@app.route('/index')
@app.route("/")
def index():
    g.db = connect_db()

    cur = g.db.execute("SELECT * FROM temperature_average ORDER BY id DESC LIMIT 30")
    temperature = []
    sum = 0
    i = 0

    for row in cur.fetchall():
        temperature.append([row[2] + 2 * 3600000, row[1]])
        sum += row[1]
        i += 1
    average_temperature = round(sum / i, 2)

    cur = g.db.execute("SELECT * FROM humidity_average ORDER BY id DESC LIMIT 30")
    humidity = []
    sum = 0
    i = 0

    for row in cur.fetchall():
        humidity.append([row[1] + 2 * 3600000, row[2]])
        sum += row[2]
        i += 1
    average_humidity = round(sum / i, 2)

    cur = g.db.execute("SELECT * FROM light_flux_average ORDER BY id DESC LIMIT 30")
    light_flux = []
    sum = 0
    i = 0

    for row in cur.fetchall():
        light_flux.append([row[1] + 2 * 3600000, row[2]])
        sum += row[2]
        i += 1
    average_light_flux = round(sum / i, 2)

    g.db.close()
    return render_template("index.html", temperature=json.dumps(temperature), average_temperature=average_temperature,
                           humidity=json.dumps(humidity), average_humidity=average_humidity,
                           light_flux=json.dumps(light_flux),
                           average_light_flux=average_light_flux)


@app.route("/live")
@app.route("/live/<refresh>")
def live(refresh=False):
    g.db = connect_db()

    cur = g.db.execute("SELECT value FROM temperature_live ORDER BY id DESC LIMIT 1")
    for row in cur.fetchall():
        current_temperature = row[0]

    cur = g.db.execute("SELECT value FROM humidity_live ORDER BY id DESC LIMIT 1")
    for row in cur.fetchall():
        current_humidity = row[0]

    cur = g.db.execute("SELECT value FROM light_flux_live ORDER BY id DESC LIMIT 1")
    for row in cur.fetchall():
        current_flux = row[0]

    cur = g.db.execute("SELECT value FROM light_on_off ORDER BY id DESC LIMIT 1")
    for row in cur.fetchall():
        current_light_on_off = row[0]

    datetime_info = get_date_and_time()
    if refresh:
        return json.dumps({"current_temperature": current_temperature, "current_humidity": current_humidity,
                           "current_flux": current_flux, "current_light_on_off": current_light_on_off,
                           "datetime_info": datetime_info})

    return render_template("live.html", current_temperature=current_temperature, current_humidity=current_humidity,
                           current_flux=current_flux, current_light_on_off=current_light_on_off,
                           datetime_info=datetime_info)


def get_date_and_time():
    API_KEY = "HWYGDEIYZWI7"
    FORMAT = "json"
    LOOKUP_METHOD = "zone"
    ZONE = "Europe/Podgorica"
    CITY = "Podgorica, ME"

    url = "http://api.timezonedb.com/v2/get-time-zone?key={0}&format={1}&by={2}&zone={3}".format(API_KEY, FORMAT,
                                                                                                 LOOKUP_METHOD, ZONE)

    try:
        response = requests.get(url, timeout=10).json()
        timestamp = response["timestamp"]
        gmtOffset = response["gmtOffset"]
        temp_format = datetime.datetime.fromtimestamp(
            int(timestamp - gmtOffset)
        ).strftime('%a, %e. %B/%H:%M')

        my_format = {
            "date": temp_format.partition('/')[0],
            "time": temp_format.partition('/')[2],
            "city": CITY
        }

    except(ConnectionError, ValueError, ConnectionAbortedError, RequestException):
        my_format = None
        print(sys.exc_info()[1])

    return my_format


@app.route("/switch_light/<param>")
def move_forward(param):

    SWITCH_LIGHT_CHANNEL = "home/room/0/light/0/"

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(SWITCH_LIGHT_CHANNEL)

    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()

    client.publish(SWITCH_LIGHT_CHANNEL, param)
    g.db = connect_db()

    current_time = datetime.datetime.now()
    current_timestamp = int(time.mktime(current_time.timetuple()))
    current_time_sqlite_format = int('{:<013}'.format(current_timestamp))

    g.db.execute("INSERT INTO light_on_off('datetime', 'value') VALUES ('%s', '%s')" % (
        current_time_sqlite_format, param))
    g.db.commit()

    return json.dumps({"success": "true"})


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == "__main__":
    app.run(debug=True)
