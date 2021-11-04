import sqlite3
from datetime import datetime
import os


if os.path.exists("sqlite.db"):
    os.remove("sqlite.db")

con = sqlite3.connect('sqlite.db')
cur = con.cursor()

with open("dbinit.sql") as f:
    q = f.read()

cur.executescript(q)
cur.execute("insert into package (shop_name, delivery_time, status, climate_optimized) "
            "values "
            "('G-Sport', ?, 'sent', false), "
            "('Komplett', ?, 'ordered', true)", (datetime.now(), datetime.now()))

for row in cur.execute("select * from package"):
    print(row)

con.commit()
con.close()
