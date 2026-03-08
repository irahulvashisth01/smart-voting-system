import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Voters table
cursor.execute("""
CREATE TABLE IF NOT EXISTS voters(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
photo TEXT,
has_voted INTEGER DEFAULT 0
)
""")

# Candidates table
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
votes INTEGER DEFAULT 0
)
""")

# Insert default candidates
cursor.execute("INSERT INTO candidates (name,votes) VALUES ('Candidate A',0)")
cursor.execute("INSERT INTO candidates (name,votes) VALUES ('Candidate B',0)")
cursor.execute("INSERT INTO candidates (name,votes) VALUES ('Candidate C',0)")

conn.commit()
conn.close()

print("Database Created Successfully")