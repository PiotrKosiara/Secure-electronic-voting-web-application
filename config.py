import datetime as dt
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback_secret_key')  # Pobieranie klucza ze zmiennych środowiskowych
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set!")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = dt.timedelta(minutes=5)
