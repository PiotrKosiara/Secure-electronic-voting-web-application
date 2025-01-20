from flask import Blueprint, render_template, session, redirect, url_for, request
from Database_interaction_functions import get_candidates, decrypt_value, hash_value
from email_verification import two_step_verification
import sqlite3

vote_blueprint = Blueprint('vote', __name__)

@vote_blueprint.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Middleware do odświeżania sesji
@vote_blueprint.before_request
def refresh_session():
    session.modified = True
    # Wymuszanie logowania
    if request.endpoint not in ['login_1.main', 'login_1.login_1'] and 'voter_id' not in session:
        return redirect(url_for('login_1.login_1'))

# Obsługa limitu żądań
@vote_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429
@vote_blueprint.route("/vote", methods=["GET", "POST"])
def vote():
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect(url_for('login_1.login_1'))  # Użytkownik musi być zalogowany

    if 'terms' not in session or not session['terms']:
        return redirect(url_for('terms.terms'))  # Użytkownik musi zaakceptować politykę

    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    try:
        # Sprawdzamy, czy użytkownik już głosował
        c.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
        has_voted = c.fetchone()
        if has_voted and has_voted[0] == 1:
            return render_template('already_voted.html')

        if request.method == 'POST':
            # Obsługa głosowania
            selected_candidate = request.form.get('candidate')
            if not selected_candidate:
                return render_template('vote.html', error_message="Please select a candidate.")

            session['selected_candidate'] = selected_candidate
            print(f"Selected candidate: {selected_candidate}")

            # Pobierz e-mail użytkownika i wyślij kod weryfikacyjny
            c.execute('SELECT email FROM voters WHERE voter_id = ?', (voter_id,))
            result = c.fetchone()
            if result:
                email = result[0]
                print(f"Email found: {email}")
                if 'verification_sent' not in session:
                    verification_code = two_step_verification(decrypt_value(email))
                    hashed_verification_code = hash_value(verification_code)
                    print("Verification email sent.")
                    c.execute('UPDATE voters SET temporary_password = ? WHERE voter_id = ?',
                              (hashed_verification_code, voter_id))
                    conn.commit()
                    session['verification_sent'] = True

                # Przekierowanie do widoku weryfikacji kodu
                return redirect(url_for('verify_code.verify_code'))
            else:
                return render_template('vote.html', error_message="Error retrieving email.")

        # Wyświetlenie listy kandydatów
        candidates = get_candidates()
        return render_template('vote.html', candidates=candidates)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return render_template('vote.html', error_message="Database error occurred.")
    finally:
        conn.close()
