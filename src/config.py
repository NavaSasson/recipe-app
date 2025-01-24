import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    if os.getenv('MONGO_USERNAME') and os.getenv('MONGO_PASSWORD'):
        MONGO_URI = (
            f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}"
            f"@{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', '27017')}"
            f"/{os.getenv('MONGO_DB', 'recipes')}?authSource={os.getenv('MONGO_AUTH_SOURCE', 'recipes')}"
            
        )
    else:
        MONGO_URI = (
            f"mongodb://{os.getenv('MONGO_HOST', 'mongo-test')}:{os.getenv('MONGO_PORT', '27017')}"
            f"/{os.getenv('MONGO_DB', 'test_recipes')}"
        )

    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    TESTING = os.getenv('TESTING', 'False') == 'True'