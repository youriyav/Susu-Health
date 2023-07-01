## backend/main.py

```python
@app.post("/users/{user_id}/transactions", response_model=TransactionRow)
async def create_transaction(user_id: int, transaction: Transaction) -> TransactionRow:
    """Adds a new transaction to the list of user transactions."""
    return transactions.create_transaction(db, user_id, transaction)
```

Il ne manquerait pas une sécurité sur un user_id inexistant ?