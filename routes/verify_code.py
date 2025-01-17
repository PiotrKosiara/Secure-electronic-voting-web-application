from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
from Database_interaction_functions import hash_value

verify_code_blueprint = Blueprint('verify_code', __name__)

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
        c.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
        has_voted = c.fetchone()
        if has_voted and has_voted[0] == 1:
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
                        c.execute('UPDATE candidates SET votes = votes + 1 WHERE name = ?', (selected_candidate,))
                        c.execute('UPDATE voters SET has_voted = 1 WHERE voter_id = ?', (voter_id,))
                        conn.commit()

                        # Czyścimy dane w sesji
                        session.pop('verification_sent', None)
                        session.pop('selected_candidate', None)

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
