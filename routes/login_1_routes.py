from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
import sqlite3
from datetime import datetime, timedelta
from Database_interaction_functions import hash_value

login_1_blueprint = Blueprint('login_1', __name__)

# Nagłówki zabezpieczające przed cofaniem i buforowaniem
@login_1_blueprint.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    return response

# Middleware do odświeżania sesji
@login_1_blueprint.before_request
def refresh_session():
    session.modified = True
    # Wymuszanie logowania
    if request.endpoint not in ['login_1.main', 'login_1.login_1'] and 'voter_id' not in session:
        return redirect(url_for('login_1.login_1'))

# Obsługa limitu żądań
@login_1_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429

@login_1_blueprint.route("/", methods=["GET", "POST"])
def main():
    return render_template('login_1.html', error_message=None)

@login_1_blueprint.route("/login_1", methods=["GET", "POST"])
def login_1():
    # Usunięcie danych sesji związanych z wcześniejszymi próbami weryfikacji
    session.pop('verification_sent', None)
    session.pop('selected_candidate', None)
    session.pop('terms', None)
    error_message = None  # Domyślnie brak błędu

    if request.method == 'POST':
        # Pobranie danych z formularza
        personal_id = request.form.get('username')
        password = request.form.get('password')

        # Połączenie z bazą danych
        conn = sqlite3.connect('voting_system.db')
        c = conn.cursor()

        # Haszowanie danych użytkownika
        hashed_personal_id = hash_value(personal_id)
        c.execute(
            'SELECT voter_id, password, has_voted, failed_attempts, last_failed_attempt FROM voters WHERE personal_id = ?',
            (hashed_personal_id,))
        result = c.fetchone()
        today = datetime.now()

        # Obsługa braku użytkownika
        if not result:
            conn.close()
            error_message = "Incorrect username or password."
            return render_template('login_1.html', error_message=error_message)

        # Pobranie danych użytkownika
        voter_id, stored_password, has_voted, failed_attempts, last_failed_attempt = result
        hashed_password = hash_value(password)

        # Konwersja daty ostatniej nieudanej próby na obiekt datetime
        if last_failed_attempt:
            last_failed_attempt = datetime.strptime(last_failed_attempt, '%Y-%m-%d %H:%M:%S')

        # Sprawdzenie blokady konta
        if failed_attempts >= 3 and last_failed_attempt:
            if today < last_failed_attempt + timedelta(minutes=1):
                conn.close()
                return render_template('login_1.html', error_message="Account temporarily blocked.")
            # Reset liczby nieudanych prób po wygaśnięciu blokady
            failed_attempts = 0
            c.execute('UPDATE voters SET failed_attempts = ? WHERE voter_id = ?', (failed_attempts, voter_id))
            conn.commit()

        # Sprawdzanie poprawności hasła
        if stored_password == hashed_password:
            # Ustawienia sesji
            session.permanent = True  # Ustalanie sesji jako trwałej
            session['voter_id'] = voter_id
            session['has_voted'] = has_voted

            # Resetowanie nieudanych prób logowania
            c.execute('UPDATE voters SET failed_attempts = 0, last_failed_attempt = NULL WHERE voter_id = ?',
                      (voter_id,))
            conn.commit()
            conn.close()

            # Przekierowanie do kolejnego kroku logowania
            return redirect(url_for('login_2.login_2'))

        else:
            # Obsługa niepoprawnego hasła
            failed_attempts += 1
            c.execute('UPDATE voters SET failed_attempts = ?, last_failed_attempt = ? WHERE voter_id = ?',
                      (failed_attempts, today.strftime('%Y-%m-%d %H:%M:%S'), voter_id))
            conn.commit()
            conn.close()
            error_message = "Incorrect username or password."
            return render_template('login_1.html', error_message=error_message)

    return render_template('login_1.html', error_message=error_message)
