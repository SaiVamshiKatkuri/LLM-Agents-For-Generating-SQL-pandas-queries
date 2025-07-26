import os

class Config:
    """
    Base configuration for the Flask application.
    """
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = 9000  # in seconds (9000 seconds = 150 minutes)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')  # Move to environment variable
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true'  # Set to True in production
    JWT_COOKIE_CSRF_PROTECT = os.environ.get('JWT_COOKIE_CSRF_PROTECT', 'False').lower() == 'true'
