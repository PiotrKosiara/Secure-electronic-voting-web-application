from flask import Flask, render_template, request, redirect, url_for
import Database_interaction_functions as db_fun


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
    return render_template('index.html', error_message=None)

@app.route("/login", methods=["POST"])
def login():
    personal_id = request.form.get('username')
    password = request.form.get('password')

    voter_id, has_voted = db_fun.verify_voter_credentials(personal_id, password)

    if voter_id is not None:
        return redirect(url_for('vote', voter_id=voter_id, has_voted=has_voted))
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
