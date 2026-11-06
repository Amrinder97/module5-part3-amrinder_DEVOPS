# backend/tests/test_conftest.py
import importlib

def test_app_imports():
    mod = importlib.import_module("app")
    assert hasattr(mod, "app")

def test_flask_app_fixture_sets_testing(flask_app):
    assert flask_app.testing is True

def test_client_fixture_can_make_requests(client):
    # Hit a definitely-missing URL so we get a deterministic 404
    resp = client.get("/__nonexistent__")
    assert resp.status_code == 404

def test_mongo_fixture_is_mongomock(flask_app):
    import app as app_module
    assert hasattr(app_module, "mongo")
    assert hasattr(app_module.mongo, "db")

    # Use bracket access for the collection name
    col = app_module.mongo.db["__test"]
    col.insert_one({"ok": 1})
    doc = col.find_one({"ok": 1})
    assert doc is not None and doc["ok"] == 1

# import pytest
# from flask_pymongo import PyMongo
# import mongomock
# import os
# import sys
# import json
# from pathlib import Path

# # Add the backend directory to the Python path
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from app import app as flask_app
# # --- Pytest Fixtures ---
# # Fixtures are functions that run before each test function to set up
# # the test environment. They help in ensuring that each test runs in
# # an isolated, clean state.

# @pytest.fixture(scope='session')
# def app():
#     """Create and configure a new app instance for each test session."""
#     flask_app.config['TESTING'] = True
#     flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
#     flask_app.config['SECRET_KEY'] = 'test-secret-key'
    
#     # Use a mock MongoDB instance for testing
#     flask_app.mongo = mongomock.MongoClient().db
    
#     # This is a temporary way to handle the PyMongo object. A better approach
#     # would be to inject the mock client directly into the PyMongo object
#     # or use a library that handles this more elegantly.
#     with flask_app.app_context():
#         # Clear collections for a clean slate
#         flask_app.mongo.users.delete_many({})
    
#     yield flask_app

# @pytest.fixture
# def client(app):
#     """A test client for the app."""
#     return app.test_client()

# @pytest.fixture
# def auth_client(client):
#     """An authenticated client fixture."""
#     # Register test user
#     client.post('/api/register', json={
#         'first_name': 'Test',
#         'last_name': 'User',
#         'email': 'test@example.com',
#         'password': 'password123'
#     })
    
#     # Login and get the access token
#     res = client.post('/api/login', json={
#         'email': 'test@example.com',
#         'password': 'password123'
#     })
#     token = res.get_json()['access_token']
    
#     # Use the token for all subsequent requests
#     client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
#     return client

# # --- Test Functions ---

# def test_app_is_created(app):
#     """Test that the Flask app is correctly created and configured."""
#     assert app is not None
#     assert app.config['TESTING'] is True
#     assert 'test_db' in app.config['MONGO_URI']

# def test_register_user(client):
#     """Test user registration endpoint with valid data."""
#     client.application.mongo.users.delete_many({})
    
#     # Print debug info
#     print("Testing registration endpoint...")
    
#     response = client.post('/api/register', json={
#         'first_name': 'John',
#         'last_name': 'Doe',
#         'email': 'john.doe@example.com',
#         'password': 'password123'
#     }, follow_redirects=False)
    
#     print(f"Status: {response.status_code}")
#     print(f"Headers: {response.headers}")
#     print(f"Data: {response.get_data(as_text=True)}")
    
#     # Verify redirect happened
#     assert response.status_code == 302
#     print(f"Redirect location: {response.headers['Location']}")
    
#     # Check if it's redirecting to itself (bad) or somewhere else
#     assert '/api/register' not in response.headers['Location'], \
#         "Endpoint is redirecting back to itself - likely a validation error"
    
#     # Verify user was created despite the redirect
#     user = client.application.mongo.users.find_one({'email': 'john.doe@example.com'})
#     assert user is not None, "User was not created in database"
#     assert user['first_name'] == 'John'

# # def test_register_user_with_existing_email(client):
# #     """Test user registration with a pre-existing email."""
# #     # First, register a user
# #     client.post('/api/register', json={
# #         'first_name': 'Jane',
# #         'last_name': 'Doe',
# #         'email': 'jane.doe@example.com',
# #         'password': 'password123'
# #     })
    
# #     # Then try to register with the same email
# #     response = client.post('/api/register', json={
# #         'first_name': 'Another',
# #         'last_name': 'User',
# #         'email': 'jane.doe@example.com',
# #         'password': 'password123'
# #     })
    
# #     assert response.status_code == 409
# #     data = response.get_json()
# #     assert 'Email already in use' in data['message']

# # def test_login_user(client):
# #     """Test user login with valid credentials."""
# #     # Register a user first
# #     client.post('/api/register', json={
# #         'first_name': 'Test',
# #         'last_name': 'User',
# #         'email': 'test_login@example.com',
# #         'password': 'password123'
# #     })
    
# #     # Now try to log in
# #     response = client.post('/api/login', json={
# #         'email': 'test_login@example.com',
# #         'password': 'password123'
# #     })
    
# #     assert response.status_code == 200
# #     data = response.get_json()
# #     assert 'access_token' in data

# # def test_login_user_invalid_credentials(client):
# #     """Test user login with incorrect password."""
# #     # Register a user first
# #     client.post('/api/register', json={
# #         'first_name': 'Test',
# #         'last_name': 'User',
# #         'email': 'test_invalid_login@example.com',
# #         'password': 'password123'
# #     })
    
# #     # Try to log in with the wrong password
# #     response = client.post('/api/login', json={
# #         'email': 'test_invalid_login@example.com',
# #         'password': 'wrong_password'
# #     })
    
# #     assert response.status_code == 401
# #     data = response.get_json()
# #     assert 'Invalid email or password' in data['message']

# # def test_protected_endpoint(auth_client):
# #     """Test a protected endpoint with an authenticated client."""
# #     response = auth_client.get('/api/protected_resource')
# #     assert response.status_code == 200
# #     data = response.get_json()
# #     assert 'message' in data
# #     assert 'user' in data