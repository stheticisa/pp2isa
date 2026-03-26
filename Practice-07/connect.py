import psycopg2
from config import load_config

def connect():
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        print("Connected to PostgreSQL!")  # <- this prints when connected
        return conn
    except Exception as e:
        print("Error:", e)

# Test connection
if __name__ == "__main__":
    connect()