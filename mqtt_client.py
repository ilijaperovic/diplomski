import paho.mqtt.client as mqtt
import datetime as datetime
import sqlite3
import time

TEMP_CHANNEL = "home/room/0/sensor/0/temp"
HUM_CHANNEL = "home/room/0/sensor/0/hum"
LUM_CHANNEL = "home/room/0/sensor/0/lum"

conn = sqlite3.connect("C:/Users/Ilija/Desktop/diplomski/diplomski.sqlite")
c = conn.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe(TEMP_CHANNEL)
    client.subscribe(HUM_CHANNEL)
    client.subscribe(LUM_CHANNEL)


def on_message(client, userdata, msg):
    current_time = datetime.datetime.now()
    current_timestamp = int(time.mktime(current_time.timetuple()))
    current_time_sqlite_format = int('{:<013}'.format(current_timestamp))

    if msg.topic == TEMP_CHANNEL:
        temperature = float(((msg.payload).decode('utf-8')).split()[0])
        c.execute("INSERT INTO temperature_live('datetime', 'value') VALUES ('%s', '%s')" % (
            current_time_sqlite_format, temperature))
        conn.commit()

    if msg.topic == HUM_CHANNEL:
        humidity = float(((msg.payload).decode('utf-8')).split()[0])
        c.execute("INSERT INTO humidity_live('datetime', 'value') VALUES ('%s', '%s')" % (
            current_time_sqlite_format, humidity))
        conn.commit()

    if msg.topic == LUM_CHANNEL:
        lumination = float(((msg.payload).decode('utf-8')).split()[0])
        c.execute("INSERT INTO light_flux_live('datetime', 'value') VALUES ('%s', '%s')" % (
            current_time_sqlite_format, lumination))
        conn.commit()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()
