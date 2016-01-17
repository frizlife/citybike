#1. Gather data into database

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

#2. Analysis

import pandas as pd
import sqlite3 as lite
import collections
import datetime

con = lite.connect('citi_bike.db')
cur = con.cursor()

df = pd.read_sql_query("Select * from available_bikes order by execution_time", con, index_col = 'execution_time')

hour_change = collections.defaultdict(int)
for col in df.columns:
    station_vals = df[col].tolist()
    station_id = col[1:] #trim the "_"
    station_change = 0
    for k,v in enumerate(station_vals):
        if k < len(station_vals) - 1:
            station_change += abs(station_vals[k] - station_vals[k+1])
    hour_change[int(station_id)] = station_change #convert the station id back to integer
	
def keywithmaxval(d):
	#Find the key with the greatest value
	return max(d, key=lambda k: d[k])

# assign the max key to max_station
max_station = keywithmaxval(hour_change)

#query sqlite for reference information
cur.execute("SELECT id, stationname, latitude, longitude FROM citibike_reference WHERE id = ?", (max_station,))
data = cur.fetchone()
print("The most active station is station id %s at %s latitude: %s longitude: %s " % data)
print("With %d bicycles coming and going in the hour between %s and %s" % (
    hour_change[max_station],
    df.index[0],
    df.index[-1]
))
#print(df.index[0])

import matplotlib.pyplot as plt

plt.bar(hour_change.keys(), hour_change.values())
plt.show()
