import os

DB_USER = os.getenv("DB_USER_BC", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD_BC", "12345")
DB_HOST = os.getenv("DB_HOST_BC", "localhost")
DB_PORT = os.getenv("DB_PORT_BC", "5432")
DB_NAME = os.getenv("DB_NAME_BC", "config_temp_db")

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "simple_secret_key"
