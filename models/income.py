from models.transaction import Transaction


class Income(Transaction):
    """
    Represents an income transaction.
    """

    def get_transaction_type(self) -> str:
        return "income"