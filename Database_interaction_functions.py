import sqlite3
import hashlib
import json
from cryptography.fernet import Fernet

def create_database():
    try:
        conn = sqlite3.connect('voting_system.db')
        with conn:
            conn.execute("DROP TABLE IF EXISTS logs;")  # Dodano dla czystości danych podczas testów

            conn.execute('''CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES voters (voter_id)
            );''')

            # Pozostałe zapytania do tworzenia tabel
            conn.execute("DROP TABLE IF EXISTS voters;")
            conn.execute("DROP TABLE IF EXISTS candidates;")
            conn.execute("DROP TABLE IF EXISTS votes;")

            conn.execute('''
                CREATE TABLE voters (
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
                CREATE TABLE candidates (
                    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    votes INTEGER DEFAULT 0
                );
            ''')

            conn.execute('''
                CREATE TABLE votes (
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

def log_action(voter_id, action, details=None):
    try:
        conn = sqlite3.connect('voting_system.db')
        with conn:
            conn.execute(
                'INSERT INTO logs (voter_id, action, details) VALUES (?, ?, ?)',
                (voter_id, action, details)
            )
            conn.commit()
            print(f"Logged action: {action} for voter_id: {voter_id}")
    except Exception as e:
        print(f"Failed to log action: {action}. Error: {str(e)}")


def get_candidates():
    try:
        conn = sqlite3.connect('voting_system.db')
        with conn:
            cursor = conn.execute("SELECT name FROM candidates;")
            candidates = [row[0] for row in cursor.fetchall()]
        return candidates
    except Exception as e:
        print("An error occurred while fetching candidates:", str(e))
        return []


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

    c.execute('SELECT password, voter_id, has_voted, failed_attempts FROM voters WHERE personal_id = ?',
              (hashed_personal_id,))
    result = c.fetchone()

    if result:
        stored_password, voter_id, has_voted, failed_attempts = result

        # Blokowanie konta po 3 nieudanych próbach
        if failed_attempts >= 3:
            log_action(voter_id, "Login Attempt", "Failed: Account locked.")
            print("Account locked due to multiple failed attempts.")
            conn.close()
            return None, None

        if stored_password == hashed_password:
            c.execute('UPDATE voters SET failed_attempts = 0 WHERE voter_id = ?', (voter_id,))
            conn.commit()
            log_action(voter_id, "Login", "Successful")
            conn.close()
            return voter_id, has_voted
        else:
            c.execute('UPDATE voters SET failed_attempts = failed_attempts + 1 WHERE voter_id = ?', (voter_id,))
            conn.commit()
            log_action(voter_id, "Login Attempt", "Failed: Incorrect password.")
            print("Invalid credentials.")
    else:
        log_action(None, "Login Attempt", "Failed: Personal ID not found.")
        print("Invalid credentials.")
    conn.close()
    return None, None


def register_voter(hashed_personal_id, hashed_password, encrypted_email):
    try:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        c.execute('INSERT INTO voters (personal_id, password, email, has_voted) VALUES (?, ?, ?, 0)',
                  (hashed_personal_id, hashed_password, encrypted_email))
        conn.commit()
        voter_id = c.lastrowid
        log_action(voter_id, "Registration", "User registered successfully.")
        print("Voter registered successfully.")
    except sqlite3.IntegrityError:
        log_action(None, "Registration", "Failed: Voter already exists.")
        print("Voter already exists.")
    finally:
        conn.close()

def view_logs():
    try:
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        c.execute('SELECT log_id, voter_id, action, details, timestamp FROM logs ORDER BY timestamp DESC')
        logs = c.fetchall()
        print("Logs:")
        for log in logs:
            print(f"ID: {log[0]}, Voter ID: {log[1]}, Action: {log[2]}, Details: {log[3]}, Time: {log[4]}")
    except Exception as e:
        print(f"Failed to retrieve logs: {str(e)}")
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
