import sqlite3
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
        if row is None:
            print("WTFFFF")
        weight, ordered_time, terminal_time, _, climate_optimized = row[1:]
        shop_name = "Komplett AS"
        zip_codes = ["3231 Oslo", "4527 Alta", "2414 Trondheim"]
        zip_code = zip_codes[random.randint(0, len(zip_codes) - 1)]
        user_id = random.randint(2, 1000)
        values.append([user_id, shop_name, ordered_time, terminal_time, terminal_time, climate_optimized, zip_code])
    for i in range(7):
        print(values[i])
        values[i][0] = 1
    values = [str(tuple(x)) for x in values]
    query("insert into package (user_id, shop_name, ordered_time, terminal_time, delivery_time, climate_optimized, zip_code) values " + ", ".join(values))

for row in cur.execute("select * from package"):
    print(row)

con.commit()
con.close()
