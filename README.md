Recipes Collection App:

 Project Structure
 recipe_app/
 ├── .env
 ├── requirements.txt
 ├── src/
 │   ├── __init__.py
 │   ├── app.py
 │   ├── config.py
 │   ├── models.py
 │   └── static/
 │       ├── index.html
 │       ├── styles.css
 │       └── script.js

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
