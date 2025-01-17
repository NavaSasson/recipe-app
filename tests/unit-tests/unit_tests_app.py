import pytest
from flask import json
from bson import ObjectId
from app import app
from models import mongo, Recipe

@pytest.fixture
def client():
    
    with app.test_client() as client:
        with app.app_context():
            mongo.init_app(app)
            # Clear the test database before each test
            mongo.db.recipes.delete_many({})
            # Initialize with default recipes
            Recipe.init_default_recipes()
        yield client

def test_get_all_recipes(client):
    """Test retrieving all recipes"""
    response = client.get('/recipe')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 3  # Based on default recipes
    
def test_create_recipe(client):
    """Test creating a new recipe"""
    new_recipe = {
        'name': 'Test Recipe',
        'category': 'breakfast',
        'ingredients': ['ingredient1', 'ingredient2'],
        'steps': ['step1', 'step2']
    }
    
    response = client.post('/recipe',
                          data=json.dumps(new_recipe),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

    # Verify the recipe was created
    created_recipe = client.get(f'/recipe/{data["id"]}')
    created_data = json.loads(created_recipe.data)
    assert created_data['name'] == new_recipe['name']

def test_create_recipe_invalid_data(client):
    """Test creating a recipe with invalid data"""
    invalid_recipe = {
        'name': 'Invalid Recipe'
        # Missing required fields
    }
    
    response = client.post('/recipe',
                          data=json.dumps(invalid_recipe),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_recipe_by_id(client):
    """Test retrieving a specific recipe"""
    # First create a recipe
    new_recipe = {
        'name': 'Test Recipe',
        'category': 'breakfast',
        'ingredients': ['ingredient1', 'ingredient2'],
        'steps': ['step1', 'step2']
    }
    
    create_response = client.post('/recipe',
                                data=json.dumps(new_recipe),
                                content_type='application/json')
    recipe_id = json.loads(create_response.data)['id']
    
    # Now retrieve it
    response = client.get(f'/recipe/{recipe_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == new_recipe['name']

def test_get_recipe_not_found(client):
    """Test retrieving a non-existent recipe"""
    non_existent_id = str(ObjectId())
    response = client.get(f'/recipe/{non_existent_id}')
    assert response.status_code == 404

def test_update_recipe(client):
    """Test updating a recipe"""
    # First create a recipe
    new_recipe = {
        'name': 'Test Recipe',
        'category': 'breakfast',
        'ingredients': ['ingredient1', 'ingredient2'],
        'steps': ['step1', 'step2']
    }
    
    create_response = client.post('/recipe',
                                data=json.dumps(new_recipe),
                                content_type='application/json')
    recipe_id = json.loads(create_response.data)['id']
    
    # Update the recipe
    updated_data = {
        'name': 'Updated Recipe Name',
        'category': 'breakfast',
        'ingredients': ['new_ingredient'],
        'steps': ['new_step']
    }
    
    response = client.put(f'/recipe/{recipe_id}',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    
    # Verify the update
    get_response = client.get(f'/recipe/{recipe_id}')
    data = json.loads(get_response.data)
    assert data['name'] == updated_data['name']

def test_delete_recipe(client):
    """Test deleting a recipe"""
    # First create a recipe
    new_recipe = {
        'name': 'Test Recipe',
        'category': 'breakfast',
        'ingredients': ['ingredient1', 'ingredient2'],
        'steps': ['step1', 'step2']
    }
    
    create_response = client.post('/recipe',
                                data=json.dumps(new_recipe),
                                content_type='application/json')
    recipe_id = json.loads(create_response.data)['id']
    
    # Delete the recipe
    response = client.delete(f'/recipe/{recipe_id}')
    assert response.status_code == 200
    
    # Verify the recipe was deleted
    get_response = client.get(f'/recipe/{recipe_id}')
    assert get_response.status_code == 404

def test_get_recipes_by_category(client):
    """Test retrieving recipes by category"""
    response = client.get('/recipe/category/breakfast')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(recipe['category'] == 'breakfast' for recipe in data)

def test_metrics_endpoint(client):
    """Test the metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200