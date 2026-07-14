import psycopg

DB_URI = "postgresql://postgres:postgres@localhost:5442/chatbot"

conn = psycopg.connect(DB_URI)

conn.autocommit = True