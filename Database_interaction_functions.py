import sqlite3
import hashlib
import json
from cryptography.fernet import Fernet

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
                    personal_id TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    temporary_password TEXT DEFAULT NULL,
                    has_voted INTEGER DEFAULT 0,
                    failed_attempts INTEGER DEFAULT 0,
                    last_failed_attempt TIMESTAMP
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
        pass
        #conn.close()


def hash_value(value):
    return hashlib.sha256(value.encode()).hexdigest()

def encrypt_value(value):
    with open('key.json', 'r') as key_file:
        stored_data = json.load(key_file)
        stored_key = stored_data['key'].encode('utf-8')
    cipher_suite = Fernet(stored_key)
    value_2 = str(value).encode()
    encrypted_value = cipher_suite.encrypt(value_2)
    return encrypted_value

def decrypt_value(encrypted_value):
    with open('key.json', 'r') as key_file:
        stored_data = json.load(key_file)
        stored_key = stored_data['key'].encode('utf-8')
    cipher_suite = Fernet(stored_key)
    decrypted_value = cipher_suite.decrypt(encrypted_value).decode()
    return decrypted_value

def verify_voter_credentials(personal_id, password):
    hashed_personal_id = hash_value(personal_id)
    hashed_password = hash_value(password)
    
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    
    c.execute('SELECT password, voter_id, has_voted FROM voters WHERE personal_id = ?', (hashed_personal_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        stored_password, voter_id, has_voted = result
        if stored_password == hashed_password:
            return voter_id, has_voted
    
    return None, None

def register_voter(hashed_personal_id, hashed_password, enctypted_email):
    try: 
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        # Store already hashed personal_id and password
        c.execute('INSERT INTO voters (personal_id, password, email, has_voted) VALUES (?, ?, ?, 0)', (hashed_personal_id, hashed_password, enctypted_email))
        conn.commit()
        print("Voter registered successfully.")
    except sqlite3.IntegrityError:
        print("Voter already exists.")
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
