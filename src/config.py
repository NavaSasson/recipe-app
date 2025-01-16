import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}?authSource=admin"
    DEBUG = os.getenv('DEBUG', 'False') == 'True'