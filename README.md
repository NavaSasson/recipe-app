# Recipes Collection App:

Application structure and how each component works:

File Structure Explanation:
Backend Files (in /src):

app.py: Main Flask application with all API endpoints
config.py: Configuration settings, including MongoDB connection
models.py: Database models and operations
__init__.py: Makes the directory a Python package

Frontend Files (in /src/static):

index.html: Main HTML page
styles.css: CSS styling
script.js: Frontend JavaScript for interacting with the API

Configuration Files:

.env: Environment variables for MongoDB connection
requirements.txt: Python dependencies

Endpoints:
- POST /recipe - Create new recipe
- GET /recipe - Get all recipes
- GET /recipe/{id} - Get specific recipe
- PUT /recipe/{id} - Update recipe
- DELETE /recipe/{id} - Delete recipe
- GET /recipe/category/{category} - Get recipes by category
- GET /metrics - Prometheus metrics

MongoDB Schema:
{
  "_id": ObjectId,
  "name": String,
  "category": String,
  "ingredients": Array,
  "steps": Array,
  "created_at": DateTime,
  "updated_at": DateTime
}


How to Run the Application:
# Option 1: with docker-compose:
Run: Run: docker-compose -f docker-compose.app.yaml up --build -d

# Option 2: 
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up MongoDB

Create a MongoDB database and user:
mongo
> use admin
> db.createUser({
    user: "admin",
    pwd: "secure_password",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})
> use recipes
> db.createUser({
    user: "admin",
    pwd: "secure_password",
    roles: [ { role: "readWrite", db: "recipes" } ]
})

# 4. Create .env file with MongoDB credentials
Copy the contents shown earlier in the .env section

# 5. Run the application
python src/app.py

Running the app by docker-compose:
docker-compose up --build

# Run Unit Tests:
Run: docker-compose -f docker-compose.unit-tests.yaml up --build -d
check that u get exit code 0 from the test container

docker-compose -f docker-compose.unit-tests.yaml down

# Run E2E Tests:
Run: docker-compose -f docker-compose.e2e.yaml up --build -d
check that u get exit code 0 from the test container

docker-compose -f docker-compose.e2e.yaml down
