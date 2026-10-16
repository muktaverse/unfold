import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

def get_connection():
    # Opens a new connection to Oracle
    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

    # Tell Oracle this connection is in Indian Standard Time (UTC+05:30)
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION SET TIME_ZONE = '+05:30'")
    cursor.close()

    return conn