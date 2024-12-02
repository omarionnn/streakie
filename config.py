import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/streakie')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    PORT = int(os.getenv('PORT', 5005))
    DEBUG = os.getenv('FLASK_ENV') != 'production'
