import sqlite3

def create_database():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    # Table of voters
    c.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            voter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    ''')

    # Table of candidates
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )
    ''')

    # Table of votes
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

def register_voter(name):
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('INSERT INTO voters (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def add_candidate(name):
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('INSERT INTO candidates (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def cast_vote(voter_id, candidate_id):
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    # Check, if voter already voted
    c.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
    result = c.fetchone()
    if result and result[0] == 0:
        # Cast vote
        c.execute('INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)', (voter_id, candidate_id))
        c.execute('UPDATE voters SET has_voted = 1 WHERE voter_id = ?', (voter_id,))
        c.execute('UPDATE candidates SET votes = votes + 1 WHERE candidate_id = ?', (candidate_id,))
        conn.commit()
        print("You voted!")
    else:
        print("You alreay cast your vote.")
    conn.close()

def show_results():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT name, votes FROM candidates')
    results = c.fetchall()
    print("Voting results:")
    for row in results:
        print(f"{row[0]}: {row[1]} votes")
    conn.close()


