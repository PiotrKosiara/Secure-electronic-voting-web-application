from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
from Database_interaction_functions import hash_value, decrypt_value, decrypt_value_shamir, encrypt_value_shamir
from email_verification import send_vote_confirmation_email  # Import funkcji wysyłania e-maila

verify_code_blueprint = Blueprint('verify_code', __name__)

@verify_code_blueprint.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Middleware do odświeżania sesji
@verify_code_blueprint.before_request
def refresh_session():
    session.modified = True
    # Wymuszanie logowania
    if request.endpoint not in ['login_1.main', 'login_1.login_1'] and 'voter_id' not in session:
        return redirect(url_for('login_1.login_1'))

# Obsługa limitu żądań
@verify_code_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429

@verify_code_blueprint.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    print("verify_codeeee!!!!")
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect(url_for('login_1.login_1'))  # Użytkownik musi być zalogowany

    conn = sqlite3.connect('voting_system.db')
    c = conn.cursor()

    try:
        # Sprawdzamy, czy użytkownik już głosował
        c.execute('SELECT has_voted, email FROM voters WHERE voter_id = ?', (voter_id,))
        voter_data = c.fetchone()
        if voter_data:
            has_voted, email = voter_data
            if has_voted == 1:
                return render_template('already_voted.html')

        if request.method == 'POST':
            print("POST")
            # Obsługa weryfikacji kodu
            entered_code = request.form.get('code')
            if not entered_code:
                return render_template('verify_code.html', error_message="Please enter the verification code.")

            entered_code_hash = hash_value(entered_code)

            c.execute('SELECT temporary_password, has_voted FROM voters WHERE voter_id = ?', (voter_id,))
            result = c.fetchone()

            if result:
                stored_code, has_voted = result
                print(stored_code)
                print(has_voted)
                if entered_code_hash == stored_code and has_voted == 0:
                    selected_candidate = session.get('selected_candidate')
                    print(selected_candidate)
                    if selected_candidate:
                        # Zapisz głos w bazie danych
                        secret = f"voter_id:{voter_id},candidate:{selected_candidate}"
                        share = encrypt_value_shamir(secret)
                        c.execute('INSERT INTO votes (voter_id, encrypted_vote) VALUES (?, ?)', (voter_id, share))
                        c.execute('UPDATE voters SET has_voted = 1 WHERE voter_id = ?', (voter_id,))
                        conn.commit()


                        if email:
                            try:
                                send_vote_confirmation_email(decrypt_value(email))
                                print(f"Potwierdzenie wysłane na adres {email}")
                            except Exception as e:
                                print(f"Błąd podczas wysyłania e-maila: {e}")

                        # Czyścimy dane w sesji
                        session.pop('verification_sent', None)
                        session.pop('selected_candidate', None)
                        session.pop('terms', None)

                        return render_template('already_voted.html')
                    else:
                        return redirect(url_for('vote.vote'))
                else:
                    return render_template('verify_code.html', error_message="Incorrect verification code.")
            else:
                return render_template('verify_code.html', error_message="Verification code not found.")

        # Wyświetlenie formularza weryfikacji
        return render_template('verify_code.html')

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return render_template('verify_code.html', error_message="Database error occurred.")
    finally:
        conn.close()
