import json
import os
import tempfile
from pathlib import Path

from models.budget import Budget
from models.expense import Expense
from models.income import Income


class FileManager:
    TRANSACTION_FIELDS = ("type", "amount", "category", "description", "date")
    BUDGET_FIELDS = ("category", "limit")

    def save_transactions(self, transactions, filename):
        data = [transaction.to_dict() for transaction in transactions]
        self._write_json(filename, data)

    def load_transactions(self, filename):
        data = self._read_json(filename, [])
        transactions = []

        for index, item in enumerate(data, start=1):
            self._validate_record(item, self.TRANSACTION_FIELDS, "transaction", index)
            transaction_type = item.get("type")
            transaction_class = self._transaction_class_for(transaction_type)
            transactions.append(transaction_class(
                item["amount"],
                item["category"],
                item["description"],
                item["date"],
            ))

        return transactions

    def save_budgets(self, budgets, filename):
        data = [budget.to_dict() for budget in budgets.values()]
        self._write_json(filename, data)

    def load_budgets(self, filename):
        data = self._read_json(filename, [])
        budgets = {}

        for index, item in enumerate(data, start=1):
            self._validate_record(item, self.BUDGET_FIELDS, "budget", index)
            budget = Budget(item["category"], item["limit"])
            budgets[budget.category] = budget

        return budgets

    @staticmethod
    def _transaction_class_for(transaction_type):
        if transaction_type == "income":
            return Income
        if transaction_type == "expense":
            return Expense
        raise ValueError(
            f"Unknown transaction type '{transaction_type}'. "
            "Expected 'income' or 'expense'."
        )

    @staticmethod
    def _read_json(filename, default):
        path = Path(filename)
        if not path.exists() or path.stat().st_size == 0:
            return default

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Could not read JSON from {path}: the file is not valid JSON."
            ) from exc

        if not isinstance(data, list):
            raise ValueError(f"Invalid JSON format in {path}: expected a list of records.")

        return data

    @staticmethod
    def _write_json(filename, data):
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
                prefix=f".{path.name}.",
                suffix=".tmp",
            ) as file:
                temp_path = Path(file.name)
                json.dump(data, file, indent=2)
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_path, path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()

    @staticmethod
    def _validate_record(record, required_fields, record_type, index):
        if not isinstance(record, dict):
            raise ValueError(
                f"Invalid {record_type} record at position {index}: expected an object."
            )

        missing_fields = [
            field for field in required_fields
            if field not in record or record[field] in (None, "")
        ]
        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ValueError(
                f"Invalid {record_type} record at position {index}: "
                f"missing required field(s): {fields}."
            )
