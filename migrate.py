import time
import datetime as datetime
import sqlite3

conn = sqlite3.connect('C:/Users/Ilija/PycharmProjects/diplomski/diplomski.sqlite')
c = conn.cursor()

today = datetime.date.today()
today_timestamp = int(time.mktime(today.timetuple()))

yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday_timestamp = int(time.mktime(yesterday.timetuple()))

today_sqlite_format = int('{:<013}'.format(today_timestamp))
yesterday_sqlite_format = int('{:<013}'.format(yesterday_timestamp))

# humidity table
average = None
c.execute("SELECT avg(value) FROM humidity_live WHERE datetime >= %s AND datetime < %s" % (yesterday_sqlite_format, today_sqlite_format))
for row in c.fetchall():
    average = row[0]

if average:
    c.execute("INSERT INTO humidity_average('date', 'value') VALUES ('%s', '%s')" % (yesterday_sqlite_format, int(average)))
    conn.commit()

# temperature table
average = None
c.execute("SELECT avg(value) FROM temperature_live WHERE datetime >= %s AND datetime < %s" % (yesterday_sqlite_format, today_sqlite_format))
for row in c.fetchall():
    average = row[0]

if average:
    c.execute("INSERT INTO temperature_average('date', 'value') VALUES ('%s', '%s')" % (yesterday_sqlite_format, int(average)))
    conn.commit()

#light_lux_average
average = None
c.execute("SELECT avg(value) FROM light_flux_live WHERE datetime >= %s AND datetime < %s" % (yesterday_sqlite_format, today_sqlite_format))
for row in c.fetchall():
    average = row[0]

if average:
    c.execute("INSERT INTO light_flux_average('date', 'value') VALUES ('%s', '%s')" % (yesterday_sqlite_format, int(average)))
    conn.commit()

conn.close()