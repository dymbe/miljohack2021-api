import sqlite3
from datetime import datetime
import os
import csv
from dbutils import query
import random


if os.path.exists("sqlite.db"):
    os.remove("sqlite.db")

con = sqlite3.connect('sqlite.db')
cur = con.cursor()

with open("dbinit.sql") as f:
    q = f.read()

cur.executescript(q)

with open("example_data.csv", "r") as f:
    reader = csv.reader(f)
    headers = next(reader)
    values = []
    for row in reader:
        weight, ordered_time, terminal_time, _, climate_optimized = row[1:]
        shop_name = "Komplett AS"
        zip_codes = ["3231 Oslo", "4527 Alta", "2414 Trondheim"]
        zip_code = zip_codes[random.randint(0, len(zip_codes) - 1)]
        value = str((shop_name, ordered_time, terminal_time, terminal_time, climate_optimized, zip_code))
        values.append(value)
    query("insert into package (shop_name, ordered_time, terminal_time, delivery_time, climate_optimized, zip_code) values " + ", ".join(values))

for row in cur.execute("select * from package"):
    print(row)

con.commit()
con.close()
