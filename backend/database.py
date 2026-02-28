import sqlite3
from datetime import date, timedelta
from shared.paths import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_usage (
            date TEXT,
            app_name TEXT,
            duration REAL,
            PRIMARY KEY (date, app_name)
        )
    """)
    conn.commit()
    conn.close() # ALWAYS close your connections

def bulk_save_usage(usage_list):
    """
    Saves a list of (app_name, duration) tuples.
    This is what your perform_sync() is looking for.
    """
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Prep the data for SQLite
    data = [(today, name, dur) for name, dur in usage_list]

    try:
        # This is the "Atomic" way to save. Fast and safe.
        cur.executemany("""
            INSERT INTO daily_usage(date, app_name, duration)
            VALUES(?,?,?)
            ON CONFLICT(date, app_name)
            DO UPDATE SET duration = excluded.duration
        """, data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Bulk save failed: {e}")
    finally:
        conn.close()

def get_today_data():
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT app_name, duration FROM daily_usage WHERE date = ?", (today,))
    rows = cur.fetchall()
    conn.close()
    return {app: duration for app, duration in rows}

def get_weekly_usage():
    today = date.today()
    week_start = today - timedelta(days=6)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT date, app_name, SUM(duration)
        FROM daily_usage
        WHERE date BETWEEN ? AND ?
        GROUP BY date, app_name
        ORDER BY date ASC
    """, (week_start.isoformat(), today.isoformat()))
    
    rows = cur.fetchall()
    conn.close()

    result = {}
    for d, app, dur in rows:
        if d not in result:
            result[d] = {}
        result[d][app] = dur
    return result

def get_monthly_usage():
    today = date.today()
    # Get the start of the current month
    month_start = today.replace(day=1).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT date, app_name, duration
        FROM daily_usage
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (month_start, today.isoformat()))
    
    rows = cur.fetchall()
    conn.close()

    result = {}
    for d, app, dur in rows:
        if d not in result:
            result[d] = {}
        result[d][app] = dur
    return result


def add_today_usage(app_name, duration):
    bulk_save_usage([(app_name, duration)])