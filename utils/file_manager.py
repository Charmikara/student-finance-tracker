import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from models.budget import Budget
from models.expense import Expense
from models.income import Income
from models.transaction import Transaction


class FileManager:
    TRANSACTION_FIELDS = ("type", "amount", "category", "description", "date")
    BUDGET_FIELDS = ("category", "limit")

    def save_transactions(
        self,
        transactions: list[Transaction],
        filename: Path | str,
    ) -> None:
        data = [transaction.to_dict() for transaction in transactions]
        self._write_json(filename, data)

    def load_transactions(self, filename: Path | str) -> list[Transaction]:
        data = self._read_json(filename, [])
        transactions: list[Transaction] = []

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

    def save_budgets(self, budgets: dict[str, Budget], filename: Path | str) -> None:
        data = [budget.to_dict() for budget in budgets.values()]
        self._write_json(filename, data)

    def load_budgets(self, filename: Path | str) -> dict[str, Budget]:
        data = self._read_json(filename, [])
        budgets: dict[str, Budget] = {}

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
    def _read_json(filename: Path | str, default: list) -> list:
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
    def _write_json(filename: Path | str, data: list) -> None:
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

    @staticmethod
    def backup_files(files: list[Path | str], backup_dir: Path | str) -> list[Path]:
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backups = []

        for filename in files:
            source = Path(filename)
            if not source.exists():
                continue

            destination = backup_path / f"{source.stem}_{timestamp}{source.suffix}"
            shutil.copy2(source, destination)
            backups.append(destination)

        return backups
