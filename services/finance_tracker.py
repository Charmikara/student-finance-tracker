from pathlib import Path

from models.transaction import Transaction
from models.expense import Expense
from models.income import Income
from models.budget import Budget
from services.report_generator import ReportGenerator
from utils.file_manager import FileManager
from utils.paths import (
    BACKUP_DIR,
    BUDGETS_FILE,
    SAMPLE_BUDGETS_FILE,
    SAMPLE_TRANSACTIONS_FILE,
    TRANSACTIONS_FILE,
)
from utils.validators import normalize_category


class FinanceTracker:
    """
    Main class responsible for storing transactions,
    managing budgets, and calculating financial summaries.
    """

    def __init__(
        self,
        transactions_file: Path | str = TRANSACTIONS_FILE,
        budgets_file: Path | str = BUDGETS_FILE,
        sample_transactions_file: Path | str = SAMPLE_TRANSACTIONS_FILE,
        sample_budgets_file: Path | str = SAMPLE_BUDGETS_FILE,
        backup_dir: Path | str = BACKUP_DIR,
        file_manager: FileManager | None = None,
    ) -> None:
        self._transactions_file = Path(transactions_file)
        self._budgets_file = Path(budgets_file)
        self._sample_transactions_file = Path(sample_transactions_file)
        self._sample_budgets_file = Path(sample_budgets_file)
        self._backup_dir = Path(backup_dir)
        self._file_manager = file_manager or FileManager()
        self._transactions: list[Transaction] = []
        self._budgets: dict[str, Budget] = {}
        self.load()

    @property
    def transactions(self) -> list[Transaction]:
        return self._transactions

    @property
    def budgets(self) -> dict[str, Budget]:
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

    def backup_current_data(self) -> list[Path]:
        return self._file_manager.backup_files(
            [self._transactions_file, self._budgets_file],
            self._backup_dir,
        )

    def load_sample_data(self) -> None:
        """
        Replace current in-memory data with sample transactions and budgets.
        Call backup_current_data() before this when replacing user data.
        """
        self._transactions = self._file_manager.load_transactions(
            self._sample_transactions_file
        )
        self._budgets = self._file_manager.load_budgets(self._sample_budgets_file)

    def clear_data(self) -> None:
        """
        Remove all current in-memory transactions and budgets.
        Call backup_current_data() before this when clearing user data.
        """
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
        return self._generate_report()["total_income"]

    def get_total_expenses(self) -> float:
        return self._generate_report()["total_expense"]

    def get_balance(self) -> float:
        return self._generate_report()["balance"]

    def get_expenses_by_category(self) -> dict[str, float]:
        return self._generate_report()["category_spending"]

    def get_budget_status(self) -> dict[str, dict[str, float | bool]]:
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

    def list_transactions(self) -> list[Transaction]:
        return self._transactions

    def _generate_report(self) -> dict[str, float | dict[str, float]]:
        return ReportGenerator().generate_report(self._transactions)
