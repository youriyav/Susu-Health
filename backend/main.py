from fastapi import FastAPI, HTTPException

from backend.db import InMemoryDB
from backend.logic import transactions
from backend.models import Transaction, TransactionState, TransactionType

app = FastAPI()

db = InMemoryDB()


@app.get("/")
async def root():
    """Simple endpoint to test if the server is up and running"""
    return {"message": "Hello World"}


@app.get("/users/{user_id}/transactions")
async def get_transactions(user_id: int):
    """Returns all transactions for a user."""
    return transactions.transactions(db, user_id)


@app.get("/users/{user_id}/transactions/balance")
async def get_balance(user_id: int):
    """Computes the balance of payments for a user subscription."""
    users_transactions = [t for t in transactions.transactions(db, user_id)]

    sums_deposits = sum(
        [
            t.amount
            for t in users_transactions
            if t.type == TransactionType.DEPOSIT
            and t.state == TransactionState.COMPLETED
        ]
    )
    sums_withdrawals = sum(
        [
            t.amount
            for t in users_transactions
            if t.type == TransactionType.SCHEDULED_WITHDRAWAL
            and t.state == TransactionState.COMPLETED
        ]
    )
    sums_refund = sum(
        [
            t.amount
            for t in users_transactions
            if t.type == TransactionType.REFUND
            and t.state in [TransactionState.COMPLETED, TransactionState.PENDING]
        ]
    )

    balance = sums_deposits - sums_withdrawals - sums_refund

    scheduled_withdrawals = [
        t
        for t in users_transactions
        if t.type == TransactionType.SCHEDULED_WITHDRAWAL
        and t.state == TransactionState.SCHEDULED
    ]

    withdrawals = []

    for transaction in sorted(scheduled_withdrawals, key=lambda t: t.date):
        coverage = min(round((balance / transaction.amount) * 100, 2), 100)
        coverage_amount = min(transaction.amount, balance)
        balance = max(balance - transaction.amount, 0)

        withdrawals.append(
            {
                "amount": transaction.amount,
                "coverage": coverage,
                "coverage_amount": coverage_amount,
                "date": transaction.date,
            }
        )

    return {"withdrawals": withdrawals, "balance": balance}


@app.get("/users/{user_id}/transactions/{transaction_id}")
async def get_transaction(user_id: int, transaction_id: int):
    """Returns a given transaction of the user."""
    transaction = transactions.transaction(db, user_id, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/users/{user_id}/transactions")
async def create_transaction(user_id: int, transaction: Transaction):
    """Adds a new transaction to the list of user transactions."""
    return transactions.create_transaction(db, user_id, transaction)
