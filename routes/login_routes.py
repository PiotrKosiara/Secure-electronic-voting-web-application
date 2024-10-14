from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from Database_interaction_functions import hash_value

login_blueprint = Blueprint('login', __name__)

@login_blueprint.before_request
def refresh_session():
    session.modified = True

@login_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429

@login_blueprint.route("/", methods=["GET", "POST"])
def main():
    return render_template('login_1.html', error_message=None)

@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        personal_id = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()

        hashed_personal_id = hash_value(personal_id)
        c.execute('SELECT voter_id, password, has_voted, failed_attempts, last_failed_attempt FROM voters WHERE personal_id = ?', (hashed_personal_id,))
        result = c.fetchone()
        today = datetime.now()

        if result:
            voter_id, stored_password, has_voted, failed_attempts, last_failed_attempt = result
            hashed_password = hash_value(password)

            if failed_attempts >= 3 and last_failed_attempt:
                if today < last_failed_attempt + datetime.timedelta(minutes=1):
                    conn.close()
                    return render_template('login_1.html', error_message="Account temporarily blocked.")
                failed_attempts = 0

            if stored_password == hashed_password:
                session.permanent = True
                session['voter_id'] = voter_id  
                session['has_voted'] = has_voted

                # Reset failed attempts after successful login
                c.execute('UPDATE voters SET failed_attempts = 0, last_failed_attempt = NULL WHERE voter_id = ?', (voter_id,))
                conn.commit()
                conn.close()

                return redirect(url_for('login_2.main'))  

            else:
                failed_attempts += 1
                c.execute('UPDATE voters SET failed_attempts = ?, last_failed_attempt = ? WHERE voter_id = ?', 
                          (failed_attempts, today.strftime('%Y-%m-%d %H:%M:%S'), voter_id))
                conn.commit()
                conn.close()
                error_message = "Incorrect username or password."
                return render_template('login_1.html', error_message=error_message)

        conn.close()
   
    return render_template('login_1.html')
