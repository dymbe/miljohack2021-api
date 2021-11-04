import sqlite3


# Very bad, does not scale
def query(*args):
    con = sqlite3.connect('sqlite.db')
    cur = con.cursor()
    result = list(cur.execute(*args))
    con.commit()
    con.close()
    return result
