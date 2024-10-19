from flask import Blueprint, render_template, request, redirect, session, url_for
import sqlite3
from Database_interaction_functions import hash_value, decrypt_value
from email_verification import two_step_verification

login_2_blueprint = Blueprint('login_2', __name__)

@login_2_blueprint.route("/", methods=["GET", "POST"])
def main():
    # voter_id = session['voter_id']
    # print(f"Voter ID from session in main: {voter_id}")  
    return render_template('login_2.html', error_code=None)

@login_2_blueprint.route("/login_2", methods=["GET", "POST"])
def login_2():
    verification_sent = two_step_verification(decrypt_value(email)) 
    if request.method == 'POST':
        secret_code = request.form.get('code')
        voter_id = session.get('voter_id')
        print(f"Voter ID from session in login_2: {voter_id}")
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()
        try:
            c.execute('SELECT email FROM voters WHERE voter_id = ?', (voter_id,))
            result = c.fetchone()
            if result:
                email = result[0]
                print(f"Email found: {email}")
                #verification_sent = two_step_verification(decrypt_value(email))  
                print(verification_sent)
                query = 'UPDATE voters SET temporary_password = ? WHERE voter_id = ?'
                c.execute(query, (hash_value(verification_sent), voter_id,))
                conn.commit()

                
                print(secret_code)
                secret_code_hash = hash_value(str(secret_code))
                c.execute('SELECT temporary_password FROM voters WHERE voter_id = ?', (voter_id,))
                dump = c.fetchone()
                if dump:
                    print("zhashowana zawartość bazy temp")
                    print(dump[0])
                    print(secret_code_hash)
                    if str(secret_code_hash) == str(dump[0]):
                        conn.close()
                        return redirect(url_for('vote.vote')) 
                    else:
                        error_code = "Incorrect e-mail verification code."
                        return render_template('login_2.html', error_code=error_code)
            else:
                print(f"No email found for voter_id: {voter_id}")
                return render_template('login_2.html', error_message="Error retrieving email.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return render_template('login_2.html', error_message="Database error occurred.")
        finally:
            conn.close()

    return render_template("login_2.html")
