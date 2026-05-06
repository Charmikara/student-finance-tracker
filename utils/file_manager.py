import json
from datetime import date
from pathlib import Path

from models.budget import Budget
from models.expense import Expense
from models.income import Income


class FileManager:
    def save_transactions(self, transactions, filename):
        data = [transaction.to_dict() for transaction in transactions]
        self._write_json(filename, data)

    def load_transactions(self, filename):
        data = self._read_json(filename, [])
        transactions = []

        for item in data:
            transaction_type = item.get("type")
            transaction_class = self._transaction_class_for(transaction_type)
            transactions.append(transaction_class(
                item.get("amount"),
                item.get("category"),
                item.get("description") or "No description",
                item.get("date") or date.today().isoformat(),
            ))

        return transactions

    def save_budgets(self, budgets, filename):
        data = [budget.to_dict() for budget in budgets.values()]
        self._write_json(filename, data)

    def load_budgets(self, filename):
        data = self._read_json(filename, [])
        budgets = {}

        for item in data:
            budget = Budget(item.get("category"), item.get("limit"))
            budgets[budget.category] = budget

        return budgets

    @staticmethod
    def _transaction_class_for(transaction_type):
        if transaction_type == "income":
            return Income
        if transaction_type == "expense":
            return Expense
        raise ValueError(f"Unknown transaction type: {transaction_type}")

    @staticmethod
    def _read_json(filename, default):
        path = Path(filename)
        if not path.exists() or path.stat().st_size == 0:
            return default

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _write_json(filename, data):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
