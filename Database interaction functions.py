import sqlite3

def create_database():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    # Tabela wyborców
    c.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            voter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    ''')

    # Tabela kandydatów
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )
    ''')

    # Tabela głosów
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER,
            candidate_id INTEGER,
            FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id)
        )
    ''')

    conn.commit()
    conn.close()

create_database()
