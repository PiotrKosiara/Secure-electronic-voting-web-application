from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from routes import login_blueprint, vote_blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Configure Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)

# Register blueprints for routes
app.register_blueprint(login_blueprint)
app.register_blueprint(vote_blueprint)

if __name__ == "__main__":
    app.run(debug=True)