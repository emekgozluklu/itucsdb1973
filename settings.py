import os


class Config:
    port = 8080


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = "postgres://postgres:docker@localhost:5432/postgres"
    SECRET_KEY = ""
