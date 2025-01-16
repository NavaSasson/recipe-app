from datetime import datetime
from flask_pymongo import PyMongo
from bson import ObjectId

mongo = PyMongo()

class Recipe:
    VALID_CATEGORIES = ['breakfast', 'lunch', 'dinner', 'cakes']  # Add new category here
    
    @staticmethod
    def create(recipe_data):
        # Add validation
        if recipe_data.get('category') not in Recipe.VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {Recipe.VALID_CATEGORIES}")
        
        recipe_data['created_at'] = datetime.utcnow()
        recipe_data['updated_at'] = datetime.utcnow()
        recipe_data['_id'] = ObjectId()
        return mongo.db.recipes.insert_one(recipe_data)

    @staticmethod
    def get_all():
        return list(mongo.db.recipes.find())

    @staticmethod
    def get_by_id(recipe_id):
        return mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})

    @staticmethod
    def get_by_category(category):
        return list(mongo.db.recipes.find({'category': category}))

    @staticmethod
    def update(recipe_id, recipe_data):
        recipe_data['updated_at'] = datetime.utcnow()
        return mongo.db.recipes.update_one(
            {'_id': ObjectId(recipe_id)},
            {'$set': recipe_data}
        )

    @staticmethod
    def delete(recipe_id):
        return mongo.db.recipes.delete_one({'_id': ObjectId(recipe_id)})

    @staticmethod
    def init_default_recipes():
        default_recipes = [
            {
                "name": "Oatmeal with Berries",
                "category": "breakfast",
                "ingredients": ["oats", "mixed berries", "honey", "milk"],
                "steps": [
                    "Bring milk to boil",
                    "Add oats and cook for 5 minutes",
                    "Top with berries and honey"
                ]
            },
            {
                "name": "Grilled Chicken Salad",
                "category": "lunch",
                "ingredients": ["chicken breast", "lettuce", "tomatoes", "cucumber", "olive oil"],
                "steps": [
                    "Grill the chicken breast",
                    "Chop vegetables",
                    "Mix all ingredients",
                    "Drizzle with olive oil"
                ]
            },
            {
                "name": "Pasta Bolognese",
                "category": "dinner",
                "ingredients": ["pasta", "ground beef", "tomato sauce", "onion", "garlic"],
                "steps": [
                    "Cook pasta according to package",
                    "Brown the meat with onion and garlic",
                    "Add tomato sauce and simmer",
                    "Combine pasta and sauce"
                ]
            }
        ]
        
        # Only insert if collection is empty
        if mongo.db.recipes.count_documents({}) == 0:
            for recipe in default_recipes:
                Recipe.create(recipe)