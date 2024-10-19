from flask import Blueprint, render_template, request, redirect, session, url_for
import sqlite3
from Database_interaction_functions import hash_value, decrypt_value
from email_verification import two_step_verification

login_2_blueprint = Blueprint('login_2', __name__)

@login_2_blueprint.route("/", methods=["GET", "POST"])
def main():
    return render_template('login_2.html', error_code=None)

@login_2_blueprint.route("/login_2", methods=["GET", "POST"])
def login_2():
    voter_id = session.get('voter_id')
    print(f"Voter ID from session in login_2: {voter_id}")
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    try:
        # Dowlanding e-mail adress from database 
        c.execute('SELECT email FROM voters WHERE voter_id = ?', (voter_id,))
        result = c.fetchone()
        if result:
            email = result[0]
            print(f"Email found: {email}")
            # Check if verification code was already send during this session
            if 'verification_sent' not in session:
                verification_sent = two_step_verification(decrypt_value(email))  
                print(f"Verification code sent: {verification_sent}")
                hashed_verification_sent = hash_value(verification_sent)
                print(f"Hashed verification_sent: {hashed_verification_sent}")
                query = 'UPDATE voters SET temporary_password = ? WHERE voter_id = ?'
                c.execute(query, (hashed_verification_sent, voter_id,))
                conn.commit()
                print("Hashed verification code saved in the database.")
                session['verification_sent'] = True
            else:
                print("Verification code already sent.")
            # Logika do obsługi formularza POST, gdzie użytkownik wprowadza kod weryfikacyjny
            if request.method == 'POST':
                secret_code = request.form.get('code')
                print(f"Secret code entered by user: {secret_code}")
                secret_code_hash = hash_value(secret_code)
                print(f"Hashed secret code entered by user: {secret_code_hash}")
                # Pobieramy kod weryfikacyjny z bazy danych i sprawdzamy
                c.execute('SELECT temporary_password FROM voters WHERE voter_id = ?', (voter_id,))
                dump = c.fetchone()
                if dump:
                    stored_temp_password = dump[0]
                    print(f"Hashed code from database (temporary_password): {stored_temp_password}")
                    if secret_code_hash == stored_temp_password:
                        print("Verification successful!")
                        conn.close()
                        # Czyścimy sesję po udanej weryfikacji
                        session.pop('verification_sent', None)
                        return redirect(url_for('vote.vote'))
                    else:
                        error_code = "Incorrect e-mail verification code."
                        print(error_code)
                        return render_template('login_2.html', error_code=error_code)
                else:
                    print("No temporary password found in database.")
                    return render_template('login_2.html', error_message="No verification code found.")
            return render_template("login_2.html")
        else:
            print(f"No email found for voter_id: {voter_id}")
            return render_template('login_2.html', error_message="Error retrieving email.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return render_template('login_2.html', error_message="Database error occurred.")
    finally:
        conn.close()
