# """
# config.py - Configuration settings for the Flask application
# """

# import os

# class Config:
#     """Base configuration"""
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/appointments.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     # Session settings
#     SESSION_TYPE = 'filesystem'
#     SESSION_PERMANENT = False
    
#     # Upload settings
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
#     # App settings
#     APP_NAME = "Doctor Appointment System"
#     APP_VERSION = "1.0.0"
    
# class DevelopmentConfig(Config):
#     """Development configuration"""
#     DEBUG = True
#     ENV = 'development'

# class ProductionConfig(Config):
#     """Production configuration"""
#     DEBUG = False
#     ENV = 'production'
    
# class TestingConfig(Config):
#     """Testing configuration"""
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

"""
config.py - Configuration settings for the Flask application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # USE THIS SIMPLE PATH - works every time!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///appointments.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # App settings
    APP_NAME = "Doctor Appointment System"
    APP_VERSION = "1.0.0"
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'