import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute("create table device_token (value varchar(255) unique)")
con.commit()
con.close()
