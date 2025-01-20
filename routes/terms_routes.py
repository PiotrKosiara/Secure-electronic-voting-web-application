from flask import Blueprint, render_template, session, redirect, url_for, request

terms_blueprint = Blueprint('terms', __name__)

@terms_blueprint.route("/terms", methods=["GET", "POST"])
def terms():
    voter_id = session.get('voter_id')
    if not voter_id:
        return redirect(url_for('login_1.login_1'))  # Użytkownik musi być zalogowany

    try:
        # Odczytanie zawartości pliku `terms.txt`
        with open('static/documents/terms.txt', 'r', encoding='utf-8') as file:
            terms_content = file.read()
    except FileNotFoundError:
        terms_content = "Terms and Conditions not available at the moment."

    if request.method == 'POST':
        # Sprawdzamy, czy użytkownik zaakceptował politykę
        agree_to_policy = request.form.get('preference')
        if agree_to_policy != 'agree':
            return render_template('terms.html', error_message="You must agree to the policy to proceed.", terms_content=terms_content)
        else:
            print("Klikniecie");
            # Ustawienie flagi w sesji
            session['terms'] = True
            return redirect(url_for('vote.vote'))  # Po zaakceptowaniu wracamy do głosowania

    return render_template('terms.html', terms_content=terms_content)
