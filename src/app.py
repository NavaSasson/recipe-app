from flask import Flask, jsonify, request, send_from_directory
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, generate_latest

import logging
from config import Config
from models import mongo, Recipe
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)

# Initialize MongoDB
mongo.init_app(app)

# Initialize Prometheus metrics
REQUESTS = Counter(
    'recipes_requests_total',
    'Total number of requests to the recipes service',
    ['method', 'endpoint']
)
RESPONSE_TIME = Histogram(
    'notes_recipes_time_seconds',
    'Response time in seconds',
    ['method', 'endpoint']
)

@app.before_first_request
def init_db():
    Recipe.init_default_recipes()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/recipe', methods=['POST'])
def create_recipe():
    try:
        data = request.get_json()
        required_fields = ['name', 'ingredients', 'steps', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        result = Recipe.create(data)
        logger.info(f"Created recipe: {data['name']}")
        return jsonify({'id': str(result.inserted_id)}), 201
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recipe/<string:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    try:
        data = request.get_json()
        result = Recipe.update(recipe_id, data)
        if result.modified_count:
            logger.info(f"Updated recipe with ID: {recipe_id}")
            return jsonify({'message': 'Recipe updated successfully'})
        logger.warning(f"Recipe not found with ID: {recipe_id}")
        return jsonify({'message': 'Recipe not found'}), 404
    except Exception as e:
        logger.error(f"Error updating recipe: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recipe/<string:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    try:
        result = Recipe.delete(recipe_id)
        if result.deleted_count:
            logger.info(f"Deleted recipe with ID: {recipe_id}")
            return jsonify({'message': 'Recipe deleted successfully'})
        logger.warning(f"Recipe not found with ID: {recipe_id}")
        return jsonify({'message': 'Recipe not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting recipe: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recipe/<string:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    try:
        recipe = Recipe.get_by_id(recipe_id)
        if recipe:
            recipe['_id'] = str(recipe['_id'])  # Convert ObjectId to string
            logger.info(f"Retrieved recipe with ID: {recipe_id}")
            return jsonify(recipe)
        logger.warning(f"Recipe not found with ID: {recipe_id}")
        return jsonify({'message': 'Recipe not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving recipe: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recipe', methods=['GET'])
def get_all_recipes():
    try:
        recipes = Recipe.get_all()
        # Convert ObjectId to string for JSON serialization
        for recipe in recipes:
            recipe['_id'] = str(recipe['_id'])
        logger.info(f"Retrieved all recipes, count: {len(recipes)}")
        return jsonify(recipes)
    except Exception as e:
        logger.error(f"Error retrieving recipes: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recipe/category/<string:category>', methods=['GET'])
def get_recipes_by_category(category):
    try:
        recipes = Recipe.get_by_category(category)
        # Convert ObjectId to string for JSON serialization
        for recipe in recipes:
            recipe['_id'] = str(recipe['_id'])
        logger.info(f"Retrieved recipes for category: {category}")
        return jsonify(recipes)
    except Exception as e:
        logger.error(f"Error retrieving recipes by category: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/metrics')
def metrics():
    logger.info("Accessing metrics endpoint")
    return generate_latest()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)