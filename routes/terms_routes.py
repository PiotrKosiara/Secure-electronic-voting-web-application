from flask import Blueprint, render_template, session, redirect, url_for, request

terms_blueprint = Blueprint('terms', __name__)

@terms_blueprint.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Middleware do odświeżania sesji
@terms_blueprint.before_request
def refresh_session():
    session.modified = True
    # Wymuszanie logowania
    if request.endpoint not in ['login_1.main', 'login_1.login_1'] and 'voter_id' not in session:
        return redirect(url_for('login_1.login_1'))

# Obsługa limitu żądań
@terms_blueprint.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429

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
