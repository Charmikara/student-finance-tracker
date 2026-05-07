from models.transaction import Transaction


class Expense(Transaction):
    """
    Represents an expense transaction.
    """

    def __init__(
        self,
        amount: float,
        category: str,
        description: str,
        date: str,
        transaction_id: str | None = None,
    ) -> None:
        super().__init__(amount, category, description, date, transaction_id)

    def get_transaction_type(self) -> str:
        return "expense"
