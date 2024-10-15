from flask import Blueprint, render_template, session, redirect, url_for
from config import Config

vote_blueprint = Blueprint('vote', __name__)

@vote_blueprint.route("/vote")
def vote():
    # if 'voter_id' not in session:
    #     return redirect(url_for('login.login'))

    voter_id = session['voter_id']
    has_voted = session.get('has_voted', 0)
    remaining_time = int(Config.PERMANENT_SESSION_LIFETIME.total_seconds())

    if has_voted:
        return render_template('already_voted.html')
    else:
        return render_template('vote.html', voter_id=voter_id, remaining_time=remaining_time)