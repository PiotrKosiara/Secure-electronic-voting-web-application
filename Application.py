from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import Database_interaction_functions
from Database_interaction_functions import hash_password

Database_interaction_functions.create_database()
Database_interaction_functions.add_candidate("Kandydat_A")
Database_interaction_functions.add_candidate("Kandydat_B")
Database_interaction_functions.register_voter("Jan", "password1")
Database_interaction_functions.register_voter("Anna", "password2")
Database_interaction_functions.show_results()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
    return render_template('index.html', error_message=None)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Connection with database
    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()
    c.execute('SELECT password, voter_id, has_voted FROM voters WHERE name = ?', (username,))
    result = c.fetchone()

    if result:
        hashed_password = hash_password(password)
        if result[0] == hashed_password:
            voter_id = result[1]
            has_voted = result[2]
            return redirect(url_for('vote', voter_id=voter_id, has_voted=has_voted))
        else:
            error_message = "Incorrect username or password."
    else:
        error_message = "Incorrect username or password."
    
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
