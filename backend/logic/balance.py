from typing import List
from backend.logic import transactions
from backend.models.interfaces import Database
from backend.models.models import (
    Balance,
    TransactionRow,
    TransactionState,
    TransactionType,
    Withdrawal,
)


def caclulate_jackpot(db: Database, user_id: int) -> Balance:
    """Return a list of next scheduled_withdrawal and what is left of the jackpot
    after all future withdrawall.
    """
    all_transactions = transactions.transactions(db, user_id)

    scheduled_withdrawal, remaining = __get_scheduled_withdrawal(all_transactions)
    return Balance(scheduled_withdrawal=scheduled_withdrawal, remaining=remaining)


def __get_scheduled_withdrawal(
    all_transactions: List[TransactionRow],
) -> List[Withdrawal]:
    scheduled_withdrawal = []
    total_amount = __get_jackpot(all_transactions)

    for transaction in all_transactions:
        if (
            transaction.type == TransactionType.SCHEDULED_WITHDRAWAL
            and transaction.state == TransactionState.SCHEDULED
        ):
            amount = transaction.amount
            covered = (
                transaction.amount
                if total_amount > transaction.amount
                else total_amount
            )
            coverage = covered / amount * 100 if covered > 0 else 0
            scheduled_withdrawal.append(
                Withdrawal(amount=amount, covered=covered, coverage=coverage)
            )
            total_amount -= amount
            if total_amount < 0:
                total_amount = 0
    return scheduled_withdrawal, total_amount


def __get_jackpot(all_transactions: List[TransactionRow]) -> int:
    total = 0

    for transaction in all_transactions:
        if (
            transaction.type == TransactionType.DEPOSIT
            and transaction.state == TransactionState.COMPLETED
        ):
            total += transaction.amount
        elif (
            transaction.type == TransactionType.SCHEDULED_WITHDRAWAL
            and transaction.state == TransactionState.COMPLETED
        ) or (
            transaction.type == TransactionType.REFUND
            and transaction.state
            in [TransactionState.COMPLETED, TransactionState.PENDING]
        ):
            total -= transaction.amount

    print(f"get_jackpot {total=}")
    return total
