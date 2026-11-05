import os
import psycopg
from psycopg.rows import dict_row
from flask import g
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.db

def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with open("schema.sql", "r") as f:
        schema = f.read()

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
            cur.execute("SELECT COUNT(*) FROM books")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute(
                    "INSERT INTO books (title, author, published) VALUES (%s, %s, %s)",
                    ("Java For Dummies", "Mary Jane", False),
                )
                
                cur.execute(
                    "INSERT INTO books (title, author, published) VALUES (%s, %s, %s)",
                    ("Python for Dummies", "John Crow", True),
                )