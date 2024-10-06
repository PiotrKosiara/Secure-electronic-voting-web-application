import sqlite3
import hashlib

def create_database():
    try:
        conn = sqlite3.connect('voting_system.db')
        with conn:
    
            conn.execute("DROP TABLE IF EXISTS voters;")
            conn.execute("DROP TABLE IF EXISTS candidates;")
            conn.execute("DROP TABLE IF EXISTS votes;")

            conn.execute('''
                CREATE TABLE IF NOT EXISTS voters (
                    voter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personal_id TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    has_voted INTEGER DEFAULT 0
                );
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    votes INTEGER DEFAULT 0
                );
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voter_id INTEGER,
                    candidate_id INTEGER,
                    FOREIGN KEY (voter_id) REFERENCES voters (voter_id),
                    FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id)
                );
            ''')
            conn.commit()
            print("Tables created successfully!")
    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_voter_credentials(personal_id, password):
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT password, voter_id, has_voted FROM voters WHERE personal_id = ?', (personal_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_password, voter_id, has_voted = result
        hashed_password = hash_password(password)
        if stored_password == hashed_password:
            return voter_id, has_voted
    return None, None

def register_voter(personal_id, password):
    try: 
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        hashed_password = hash_password(password)
        c.execute('INSERT INTO voters (personal_id, password, has_voted) VALUES (?, ?, 0)', (personal_id, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Voter '{personal_id}' already exists.")
    finally:
        conn.close()

def add_candidate(name):
    try:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        c.execute('INSERT INTO candidates (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Candidates '{name}' already exists.")
    finally:
        conn.close()

def cast_vote(voter_id, candidate_id):
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
    result = c.fetchone()
    if result and result[0] == 0:
        c.execute('INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)', (voter_id, candidate_id))
        c.execute('UPDATE voters SET has_voted = 1 WHERE voter_id = ?', (voter_id,))
        c.execute('UPDATE candidates SET votes = votes + 1 WHERE candidate_id = ?', (candidate_id,))
        conn.commit()
        print("You voted!")
    else:
        print("You already cast your vote.")
    conn.close()

def show_results():
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    c.execute('SELECT personal_id FROM voters')
    voters_results = c.fetchall()

    print("Voters:")
    for voter in voters_results:
        print(f"{voter[0]}")

    c.execute('SELECT name, votes FROM candidates')
    results = c.fetchall()
    print("Voting results:")
    for row in results:
        print(f"{row[0]}: {row[1]} votes")
    conn.close()
