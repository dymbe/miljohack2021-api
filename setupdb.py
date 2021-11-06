import json
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

with open("post_data.json") as f:
    post_data = json.loads(f.read())

print(post_data)

zip_codes = [max(0, (4 - len(code))) * "0" + f"{code} {post_data[code]['poststed']}" for code in post_data]
weights = [post_data[code]["weight"] for code in post_data]

with open("example_data.csv", "r") as f:
    reader = csv.reader(f)
    headers = next(reader)
    values = []
    for row in reader:
        weight, ordered_time, terminal_time, _, climate_optimized = row[1:]
        shop_name = "Komplett AS"
        zip_code = random.choices(zip_codes, weights, k=1)[0]
        user_id = random.randint(2, 1000)
        values.append([user_id, shop_name, ordered_time, terminal_time, terminal_time, climate_optimized, zip_code])
    for i in range(7):
        values[i][-2] = False
        values[i][0] = 1
    values = [str(tuple(x)) for x in values]
    query("insert into package (user_id, shop_name, ordered_time, terminal_time, delivery_time, climate_optimized, zip_code) values " + ", ".join(values))

for row in cur.execute("select * from package"):
    print(row)

con.commit()
con.close()
