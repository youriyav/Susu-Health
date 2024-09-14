from typing import List

from fastapi import FastAPI, HTTPException

from backend.db import InMemoryDB
from backend.logic import transactions, users
from backend.models import Transaction, TransactionRow
from backend.models import (
    TransactionState,
    TransactionBalanceRow,
    TransactionType,
)

app = FastAPI()

db = InMemoryDB()


@app.get("/")
async def root():
    """Simple endpoint to test if the server is up and running"""
    return {"message": "Hello World"}


@app.get("/users/{user_id}/transactions", response_model=List[TransactionRow])
async def get_transactions(user_id: int) -> List[TransactionRow]:
    """Returns all transactions for a user."""
    return transactions.transactions(db, user_id)


@app.get("/users/{user_id}/transactions/balance", response_model=dict)
async def get_balance(user_id: int) -> dict:  # pylint: disable=unused-argument
    """Computes the balance of payments for a user subscription."""
    # We expect you to write this function
    return_list = []
    list_of_transaction = transactions.transactions_by_type(
        db,
        user_id,
        type_of_transaction=TransactionType.SCHEDULED_WITHDRAWAL,
        state_of_transaction=TransactionState.SCHEDULED,
    )
    solde = transactions.get_cagnotte(db, user_id)
    print(f"solde : {solde}")
    global_rate = 0
    for transaction in list_of_transaction:
        _amount_preleve, _amount_couvert, _rate = transactions.get_transaction_balance(
            solde, transaction
        )
        transaction_balance = TransactionBalanceRow(
            amount_preleve=_amount_preleve, amount_couvert=_amount_couvert, rate=_rate
        )
        global_rate += _rate
        return_list.append(transaction_balance)
        if solde > 0:
            solde -= transaction.amount
    cagnotte = 0
    # si le solde permet de tout gérer
    if (global_rate / 100) == len(list_of_transaction):
        cagnotte = solde
    else:
        cagnotte = 0
    return {"datas": return_list, "solde_cagnotte": cagnotte}


@app.get(
    "/users/{user_id}/transactions/{transaction_id}", response_model=TransactionRow
)
async def get_transaction(user_id: int, transaction_id: int) -> TransactionRow:
    """Returns a given transaction of the user."""
    if users.user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    transaction = transactions.transaction(db, user_id, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/users/{user_id}/transactions", response_model=TransactionRow)
async def create_transaction(user_id: int, transaction: Transaction) -> TransactionRow:
    """Adds a new transaction to the list of user transactions."""
    return transactions.create_transaction(db, user_id, transaction)
