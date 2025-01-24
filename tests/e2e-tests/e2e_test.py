import pytest
import requests
import time
from typing import Dict

# Configuration
BASE_URL = "http://nginx"
WAIT_SECONDS = 30

# Global variable to store created recipe ID
created_recipe_id = None

def wait_for_services():
    """Wait for services to be ready"""
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{BASE_URL}/recipe")
            if response.status_code == 200:
                return
        except requests.RequestException:
            if time.time() - start_time > WAIT_SECONDS:
                raise TimeoutError("Services did not become ready in time")
            time.sleep(1)

@pytest.fixture(scope="session", autouse=True)
def setup_services():
    """Setup fixture to ensure services are ready before tests"""
    wait_for_services()

@pytest.fixture
def sample_recipe() -> Dict:
    """Fixture providing a sample recipe"""
    return {
        "name": "Test Recipe",
        "category": "dinner",
        "ingredients": ["ingredient1", "ingredient2"],
        "steps": ["step1", "step2"]
    }

def test_create_recipe(sample_recipe):
    """Test POST /recipe endpoint"""
    global created_recipe_id
    response = requests.post(f"{BASE_URL}/recipe", json=sample_recipe)
    assert response.status_code == 201
    assert "id" in response.json()
    created_recipe_id = response.json()["id"]  # Store ID for other tests
    assert created_recipe_id is not None

def test_get_recipe(sample_recipe):
    """Test GET /recipe/{id} endpoint"""
    assert created_recipe_id is not None  # Make sure we have an ID to test with
    response = requests.get(f"{BASE_URL}/recipe/{created_recipe_id}")
    assert response.status_code == 200
    recipe_data = response.json()
    assert recipe_data["name"] == sample_recipe["name"]
    assert recipe_data["category"] == sample_recipe["category"]

def test_update_recipe(sample_recipe):
    """Test PUT /recipe/{id} endpoint"""
    assert created_recipe_id is not None
    updated_recipe = sample_recipe.copy()
    updated_recipe["name"] = "Updated Recipe Name"
    response = requests.put(f"{BASE_URL}/recipe/{created_recipe_id}", json=updated_recipe)
    assert response.status_code == 200
    
    # Verify the update
    response = requests.get(f"{BASE_URL}/recipe/{created_recipe_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Recipe Name"

def test_delete_recipe(sample_recipe):
    """Test DELETE /recipe/{id} endpoint"""
    assert created_recipe_id is not None
    response = requests.delete(f"{BASE_URL}/recipe/{created_recipe_id}")
    assert response.status_code == 200
    
    # Verify the deletion
    response = requests.get(f"{BASE_URL}/recipe/{created_recipe_id}")
    assert response.status_code == 404

def test_get_all_recipes():
    """Test GET /recipe endpoint"""
    response = requests.get(f"{BASE_URL}/recipe")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_recipes_by_category(sample_recipe):
    """Test GET /recipe/category/{category} endpoint"""
    response = requests.get(f"{BASE_URL}/recipe/category/{sample_recipe['category']}")
    assert response.status_code == 200
    recipes = response.json()
    assert isinstance(recipes, list)
    assert all(recipe["category"] == sample_recipe["category"] for recipe in recipes)

def test_invalid_recipe_creation():
    """Test creating recipe with invalid data"""
    invalid_recipe = {"name": "Invalid Recipe"}  # Missing required fields
    response = requests.post(f"{BASE_URL}/recipe", json=invalid_recipe)
    assert response.status_code == 400

def test_invalid_recipe_id():
    """Test accessing non-existent recipe"""
    non_existent_id = "507f1f77bcf86cd799439011"
    response = requests.get(f"{BASE_URL}/recipe/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["message"] == "Recipe not found"

def test_metrics_endpoint(client):
    """Test the metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200