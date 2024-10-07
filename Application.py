
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import datetime as dt
from Database_interaction_functions import hash_value
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configure Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)

# Error handler for 429 Too Many Requests
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429

@app.route("/", methods=["GET", "POST"])

# custom limits
# @limiter.limit("2 per 1 minutes", override_defaults=False)

def main():
    return render_template('index.html', error_message=None)

@app.route("/login", methods=["POST"])
def login():
    personal_id = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    hashed_personal_id = hash_value(personal_id)

    c.execute('SELECT voter_id, password, has_voted, failed_attempts, last_failed_attempt FROM voters WHERE personal_id = ?', (hashed_personal_id,))
    result = c.fetchone()
    today = dt.datetime.now()

    if result:
        voter_id, stored_password, has_voted, failed_attempts, last_failed_attempt = result
        hashed_password = hash_value(password)

        # Check if the user is blocked
        if failed_attempts >= 3 and last_failed_attempt:
            block_time = dt.datetime.strptime(last_failed_attempt, '%Y-%m-%d %H:%M:%S')
            
            if today < block_time + dt.timedelta(minutes=1):
                error_message = "Your account is temporarily blocked due to too many failed login attempts. Please try again later."
                conn.close()
                return render_template('index.html', error_message=error_message)
            else:
                # Reset failed attempts after block time has passed
                failed_attempts = 0

        if stored_password == hashed_password:
            # Successful login, reset failed attempts
            c.execute('UPDATE voters SET failed_attempts = 0, last_failed_attempt = NULL WHERE voter_id = ?', (voter_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('vote', voter_id=voter_id, has_voted=has_voted))
        else:
            # Increment failed attempts
            failed_attempts += 1
            c.execute('UPDATE voters SET failed_attempts = ?, last_failed_attempt = ? WHERE voter_id = ?', 
                      (failed_attempts, today.strftime('%Y-%m-%d %H:%M:%S'), voter_id))
            conn.commit()
            conn.close()
            error_message = "Incorrect username or password."
            return render_template('index.html', error_message=error_message)
    else:
        error_message = "Incorrect username or password."
        conn.close()
        return render_template('index.html', error_message=error_message)


@app.route("/vote")
def vote():
    voter_id = request.args.get('voter_id', type=int)
    has_voted = request.args.get('has_voted', type=int)

    if has_voted:
        return render_template('already_voted.html')
    else:
        return render_template('vote.html', voter_id=voter_id)

if __name__ == "__main__":
    app.run(debug=True)
