import os


class Config:
    port = 8080
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    WTF_CSRF_ENABLED = True
