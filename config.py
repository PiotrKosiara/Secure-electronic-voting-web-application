import datetime as dt

class Config:
    SECRET_KEY = 'your_secret_key'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = dt.timedelta(minutes=5)