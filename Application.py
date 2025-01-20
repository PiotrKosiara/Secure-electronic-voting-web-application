from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from routes import login_1_blueprint, vote_blueprint, login_2_blueprint, verify_code_blueprint, terms_blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Redis URL (domyślnie Redis działa na localhost:6379)
REDIS_URL = "redis://localhost:6379/0"

# Configure Flask-Limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,  # Redis jako backend
    app=app,
    default_limits=["5 per minute"]
)

# Register blueprints for routes
app.register_blueprint(login_1_blueprint)
app.register_blueprint(vote_blueprint)
app.register_blueprint(login_2_blueprint)
app.register_blueprint(verify_code_blueprint)
app.register_blueprint(terms_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
