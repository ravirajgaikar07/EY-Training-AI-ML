import sqlite3

DB_PATH = "tickets.db"

def fetch_all_tickets():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Get column names
        cur.execute("PRAGMA table_info(tickets)")
        columns = [info[1] for info in cur.fetchall()]
        print("Columns:", columns)

        # Fetch all rows
        cur.execute("SELECT * FROM tickets")
        rows = cur.fetchall()
        print("Rows fetched:", len(rows))

        conn.close()

        # Combine column names and rows as list of dicts
        data = [dict(zip(columns, row)) for row in rows]
        return data
    except Exception as e:
        print("Error:", e)
        return []

# Example usage
tickets = fetch_all_tickets()
for t in tickets:
    print(t)
