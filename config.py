import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret')  # Use an environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///store.db')  # Use an environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('app', 'static', 'images')  # Path to upload folder
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

