from models.expense import Expense
from models.income import Income
from models.budget import Budget
from utils.file_manager import FileManager
from utils.validators import normalize_category


class FinanceTracker:
    """
    Main class responsible for storing transactions,
    managing budgets, and calculating financial summaries.
    """

    def __init__(
        self,
        transactions_file: str = "data/transactions.json",
        budgets_file: str = "data/budgets.json",
        sample_transactions_file: str = "data/sample_transactions.json",
        sample_budgets_file: str = "data/sample_budgets.json",
        file_manager: FileManager | None = None,
    ) -> None:
        self._transactions_file = transactions_file
        self._budgets_file = budgets_file
        self._sample_transactions_file = sample_transactions_file
        self._sample_budgets_file = sample_budgets_file
        self._file_manager = file_manager or FileManager()
        self._transactions = []
        self._budgets = {}
        self.load()

    @property
    def transactions(self) -> list:
        return self._transactions

    @property
    def budgets(self) -> dict:
        return self._budgets

    def add_income(self, amount: float, category: str, description: str, date: str) -> None:
        income = Income(amount, category, description, date)
        self._transactions.append(income)

    def add_expense(self, amount: float, category: str, description: str, date: str) -> None:
        expense = Expense(amount, category, description, date)
        self._transactions.append(expense)

    def add_budget(self, category: str, limit: float) -> None:
        budget = Budget(category, limit)
        self._budgets[normalize_category(budget.category)] = budget

    def load(self) -> None:
        self._transactions = self._file_manager.load_transactions(self._transactions_file)
        self._budgets = self._file_manager.load_budgets(self._budgets_file)

    def save(self) -> None:
        self._file_manager.save_transactions(self._transactions, self._transactions_file)
        self._file_manager.save_budgets(self._budgets, self._budgets_file)

    def load_sample_data(self) -> None:
        self._transactions = self._file_manager.load_transactions(
            self._sample_transactions_file
        )
        self._budgets = self._file_manager.load_budgets(self._sample_budgets_file)

    def clear_data(self) -> None:
        self._transactions = []
        self._budgets = {}

    def delete_transaction_by_index(self, index: int) -> None:
        if not isinstance(index, int):
            raise TypeError("Transaction index must be an integer.")

        if index < 0 or index >= len(self._transactions):
            raise IndexError("Transaction index is out of range.")

        del self._transactions[index]

    def delete_budget(self, category: str) -> None:
        normalized_category = normalize_category(category)
        if normalized_category not in self._budgets:
            raise KeyError(f"Budget not found for category: {normalized_category}")

        del self._budgets[normalized_category]

    def get_total_income(self) -> float:
        return sum(
            transaction.amount
            for transaction in self._transactions
            if transaction.get_transaction_type() == "income"
        )

    def get_total_expenses(self) -> float:
        return sum(
            transaction.amount
            for transaction in self._transactions
            if transaction.get_transaction_type() == "expense"
        )

    def get_balance(self) -> float:
        return self.get_total_income() - self.get_total_expenses()

    def get_expenses_by_category(self) -> dict:
        category_totals = {}

        for transaction in self._transactions:
            if transaction.get_transaction_type() == "expense":
                category = normalize_category(transaction.category)
                category_totals[category] = category_totals.get(category, 0) + transaction.amount

        return category_totals

    def get_budget_status(self) -> dict:
        category_spending = self.get_expenses_by_category()
        status = {}

        for category, budget in self._budgets.items():
            normalized_category = normalize_category(category)
            spent = category_spending.get(normalized_category, 0)
            remaining = budget.limit - spent

            status[normalized_category] = {
                "limit": budget.limit,
                "spent": spent,
                "remaining": remaining,
                "exceeded": spent > budget.limit
            }

        return status

    def list_transactions(self) -> list:
        return self._transactions
