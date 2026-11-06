# backend/tests/conftest.py
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import mongomock
import pytest

# Ensure the backend (where app.py lives) is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../backend
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the application module (expects backend/app.py with `app` and `mongo`)
import app as app_module


@pytest.fixture
def flask_app():
    """
    Produce a Flask app configured for testing and patch module-level `mongo`
    to use an in-memory mongomock DB so CI doesn't need a real Mongo.
    """
    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test_secret_key",
        MONGO_URI=os.environ.get(
            "MONGO_URI", "mongodb://localhost:27017/test_db?authSource=admin"
        ),
    )

    # Patch the module's `mongo` to mimic Flask-PyMongo shape: object with `.db`
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["test_db"]
    app_module.mongo = SimpleNamespace(db=mock_db)

    yield app_module.app


@pytest.fixture
def client(flask_app):
    """
    Flask test client with an application context; wipe any leftover collections.
    """
    with flask_app.test_client() as c:
        with flask_app.app_context():
            for name in list(app_module.mongo.db.list_collection_names()):
                app_module.mongo.db[name].delete_many({})
        yield c
