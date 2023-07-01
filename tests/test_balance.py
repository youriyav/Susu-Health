from fastapi.testclient import TestClient

from backend.main import app
from backend.models.models import Balance

client = TestClient(app)


def test_empty_balance():
    response = client.get("/users/4/transactions/balance")

    assert response.status_code == 200
    balance = Balance(**response.json())

    assert balance.scheduled_withdrawal[0].amount == 20
    assert balance.scheduled_withdrawal[0].covered == 20
    assert balance.scheduled_withdrawal[0].coverage == 100

    assert balance.scheduled_withdrawal[1].amount == 20
    assert balance.scheduled_withdrawal[1].covered == 20
    assert balance.scheduled_withdrawal[1].coverage == 100

    assert balance.scheduled_withdrawal[2].amount == 20
    assert balance.scheduled_withdrawal[2].covered == 5
    assert balance.scheduled_withdrawal[2].coverage == 25

    assert balance.scheduled_withdrawal[3].amount == 20
    assert balance.scheduled_withdrawal[3].covered == 0
    assert balance.scheduled_withdrawal[3].coverage == 0
