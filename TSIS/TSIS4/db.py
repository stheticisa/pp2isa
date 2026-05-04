import psycopg2
from datetime import datetime

def connect_db():
    return psycopg2.connect(
        dbname="snake_db",
        user="postgres",
        password="yourpassword",
        host="localhost",
        port="5432"
    )

def save_result(username, score, level):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;", (username,))
    conn.commit()

    cur.execute("SELECT id FROM players WHERE username=%s;", (username,))
    player_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached, played_at)
        VALUES (%s, %s, %s, %s);
    """, (player_id, score, level, datetime.now()))
    conn.commit()

    cur.close()
    conn.close()

def get_leaderboard(limit=10):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        ORDER BY g.score DESC
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_personal_best(username):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT MAX(score) FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        WHERE p.username=%s;
    """, (username,))
    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best or 0
