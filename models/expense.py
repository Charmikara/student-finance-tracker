from models.transaction import Transaction


class Expense(Transaction):
    """
    Represents an expense transaction.
    """

    def get_transaction_type(self) -> str:
        return "expense"