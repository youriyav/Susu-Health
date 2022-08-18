from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture
def deposit_transaction():
    return {
        "amount": 10.5,
        "type": "deposit",
        "date": date.today().strftime("%Y-%m-%d"),
    }


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_get_transactions():
    response = client.get("users/1/transactions")
    assert response.status_code == 200
    for transaction in response.json():
        assert transaction["user_id"] == 1


def test_get_existing_transaction():
    response = client.get("users/1/transactions/1")
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["user_id"] == 1
    assert transaction["id"] == 1


def test_get_nonexisting_transaction():
    response = client.get("users/1/transactions/9999")
    assert response.status_code == 404


def test_create_transaction(deposit_transaction):
    response = client.post("users/2/transactions", json=deposit_transaction)
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["user_id"] == 2
    assert transaction["amount"] == 10.5
    assert transaction["type"] == "deposit"
    assert transaction["date"] == date.today().isoformat()
    assert transaction["state"] == "pending"


def test_get_balance():
    response = client.get("/users/1/transactions/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 0
    assert len(data["withdrawals"]) == 3
    assert data["withdrawals"][0]["amount"] == 20
    assert data["withdrawals"][1]["amount"] == 20
    assert data["withdrawals"][2]["amount"] == 300
    assert data["withdrawals"][0]["coverage"] == 100
    assert data["withdrawals"][1]["coverage"] == 100
    assert data["withdrawals"][2]["coverage"] == 5.67
    assert data["withdrawals"][0]["coverage_amount"] == 20
    assert data["withdrawals"][1]["coverage_amount"] == 20
    assert data["withdrawals"][2]["coverage_amount"] == 17


def test_get_balance_user_not_exist():
    response = client.get("/users/111/transactions/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 0
    assert len(data["withdrawals"]) == 0
