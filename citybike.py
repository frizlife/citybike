import time
from dateutil.parser import parse
import collections
import sqlite3 as lite
import requests


con = lite.connect('citi_bike.db')
cur = con.cursor()
#cur.execute('delete from available_bikes')

for i in range(60):
    r = requests.get('http://www.citibikenyc.com/stations/json')
    exec_time = parse(r.json()['executionTime']).strftime('%Y-%m-%d-%H-%M-%S')

    cur.execute('INSERT INTO available_bikes (execution_time) VALUES (?)', (exec_time,))

    for station in r.json()['stationBeanList']:
        cur.execute("UPDATE available_bikes SET _%d = %d WHERE execution_time = '%s'" % (station['id'], station['availableBikes'], exec_time))
    con.commit()

    time.sleep(60)

con.close() #close the database connection when done