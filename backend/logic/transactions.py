from typing import List

from backend.models import (
    Transaction,
    TransactionRow,
    TransactionState,
    TransactionType,
)
from backend.models.interfaces import Database


def transactions(db: Database, user_id: int) -> List[TransactionRow]:
    """
    Returns all transactions of a user.
    """
    return [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id
    ]


# methode permettant de recupérer les transaction pour un type donné
def transactions_by_type(
    db: Database, user_id: int, type_of_transaction: str
) -> List[TransactionRow]:
    """
    Returns all transactions of a user.
    """
    return [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id and transaction.type == type_of_transaction
    ]  # methode permettant de recupérer les transaction pour un type donné


def transactions_by_type(
    db: Database, user_id: int, type_of_transaction: str, state_of_transaction: str
) -> List[TransactionRow]:
    """
    Returns all transactions of a user.
    """
    return [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id
        and transaction.state == state_of_transaction
        and transaction.type == type_of_transaction
    ]


def transaction(db: Database, user_id: int, transaction_id: int) -> TransactionRow:
    """
    Returns a given transaction of the user
    """
    transaction = db.get("transactions", transaction_id)
    return transaction if transaction and transaction.user_id == user_id else None


def create_transaction(
    db: Database, user_id: int, transaction: Transaction
) -> TransactionRow:
    """
    Creates a new transaction (adds an ID) and returns it.
    """
    if transaction.type in (TransactionType.DEPOSIT, TransactionType.REFUND):
        initial_state = TransactionState.PENDING
    elif transaction.type == TransactionType.SCHEDULED_WITHDRAWAL:
        initial_state = TransactionState.SCHEDULED
    else:
        raise ValueError(f"Invalid transaction type {transaction.type}")
    transaction_row = TransactionRow(
        user_id=user_id, **transaction.dict(), state=initial_state
    )
    return db.put("transactions", transaction_row)


"""cette fontion permet de retourner à partir du solde et de la transaction donnés
un tuplet contenant le :
-le montant du prélèvement
-le montant couvert par le solde actuel
-le taux (en pourcent, entre 0 et 100) de couverture du montant
"""


def get_cagnotte(db: Database, user_id: int) -> float:
    global_amount = 0
    list_of_complete_deposit = transactions_by_type(
        db,
        user_id,
        type_of_transaction=TransactionType.DEPOSIT,
        state_of_transaction=TransactionState.COMPLETED,
    )
    list_of_complete_withdraw = transactions_by_type(
        db,
        user_id,
        type_of_transaction=TransactionType.SCHEDULED_WITHDRAWAL,
        state_of_transaction=TransactionState.COMPLETED,
    )
    list_of_complete_refund = transactions_by_type(
        db,
        user_id,
        type_of_transaction=TransactionType.REFUND,
        state_of_transaction=TransactionState.COMPLETED,
    )
    list_of_pending_refund = transactions_by_type(
        db,
        user_id,
        type_of_transaction=TransactionType.REFUND,
        state_of_transaction=TransactionState.PENDING,
    )

    for transaction in list_of_complete_deposit:
        global_amount += transaction.amount
    for transaction in list_of_complete_withdraw:
        global_amount -= transaction.amount
    for transaction in list_of_complete_refund:
        global_amount -= transaction.amount
    for transaction in list_of_pending_refund:
        global_amount -= transaction.amount
    return global_amount


def get_transaction_balance(solde: float, transaction: TransactionRow) -> tuple:
    covert_amount = 0
    rate_amount = 0
    amount_preleve = 0
    if solde > 0:
        if solde - transaction.amount > 0:
            covert_amount = transaction.amount
            rate_amount = 100
        else:
            covert_amount = transaction.amount - abs(solde - transaction.amount)
            rate_amount = (covert_amount * 100) / transaction.amount
    else:
        rate_amount: 0
        covert_amount = 0
    return (transaction.amount, covert_amount, rate_amount)
