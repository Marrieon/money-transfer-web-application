import os
from dotenv import load_dotenv
from datetime import timedelta
from celery.schedules import crontab

load_dotenv()

class Config:
    """Base configuration class that all other configs inherit from."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- JWT Extended Configuration ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))

    # --- Cache Configuration ---
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # --- Twilio Configuration (for SMS) ---
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

    # --- Celery Configuration ---
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    
    # --- Celery Beat Schedule ---
    CELERY_BEAT_SCHEDULE = {
        'check-overdue-loans-every-day': {
            'task': 'app.tasks.social_tasks.check_overdue_loans',
            'schedule': crontab(minute=0, hour=0),
        },
    }

    # --- Flask-Limiter Configuration (MODIFIED) ---
    # NEW (The Fix): Explicitly tell Flask-Limiter to use our Redis server.
    # This makes the rate limiting robust and ready for production.
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL')
    
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    RATELIMIT_ENABLED = False


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
    CACHE_TYPE = 'SimpleCache'
    # This setting disables the rate limiter during tests, so we don't need a storage URI here.
    RATELIMIT_ENABLED = False
    CELERY_TASK_ALWAYS_EAGER = True


class ProductionConfig(Config):
    """Production-specific configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


# A dictionary to easily access the config classes by name.
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}