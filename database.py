import psycopg2
import os


def db_exec(command, params):
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(command, params)

    cursor.close()
    conn.close()


def db_fetchall(command):
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    cursor = conn.cursor()
    cursor.execute(command)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
