import sqlite3

# Connect (or create) the database file
conn = sqlite3.connect('intel_sleuth.db')
cursor = conn.cursor()

# Create the table the app is crying for
cursor.execute('''
CREATE TABLE IF NOT EXISTS osint_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    query_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Save and close
conn.commit()
conn.close()

print("intel_sleuth.db created with osint_queries table inside.")
