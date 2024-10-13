import datetime as dt

class Config:
    SECRET_KEY = 'your_secret_key'
    PERMANENT_SESSION_LIFETIME = dt.timedelta(minutes=5)