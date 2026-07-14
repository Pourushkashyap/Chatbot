from database.db import conn

cur = conn.cursor()

cur.execute('SELECT NOW();')
print(cur.fetchone())