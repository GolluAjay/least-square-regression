# config.py
import os

class Config:
    DEBUG = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'sav', 'datatab'}

