from pydoc import cli
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_empty_balance():
    response = client.get("/users/4/transactions/balance")

    assert response.status_code == 200
