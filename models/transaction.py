from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from utils.validators import normalize_category


class Transaction(ABC):
    """
    Base class for all financial transactions.
    Stores: amount, category, description, date, etc
    """

    def __init__(
        self,
        amount: float,
        category: str,
        description: str,
        date: str,
        transaction_id: str | None = None,
    ) -> None:
        self._transaction_id = self._validate_transaction_id(transaction_id)
        self._amount = self._validate_amount(amount)
        self._category = normalize_category(category)
        self._description = self._validate_text_field(description, "description")
        self._date = self._validate_date(date)

    @staticmethod
    def _validate_transaction_id(transaction_id: str | None) -> str:
        if transaction_id is None:
            return str(uuid4())

        if not isinstance(transaction_id, str):
            raise TypeError("Transaction ID must be a string.")

        cleaned_id = transaction_id.strip()
        if not cleaned_id:
            raise ValueError("Transaction ID cannot be empty.")

        return cleaned_id

    @staticmethod
    def _validate_amount(amount: float) -> float:
        """
        Ensure the amount is a positive number.
        """
        
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")

        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        return float(amount)

    @staticmethod
    def _validate_text_field(value: str, field_name: str) -> str:
        """
        Ensure a text field is a non-empty string.
        """
        if not isinstance(value, str):
            raise TypeError(f"{field_name.capitalize()} must be a string.")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name.capitalize()} cannot be empty.")

        return cleaned_value

    @staticmethod
    def _validate_date(date_str: str) -> str:
        """
        Ensure the date is in YYYY-MM-DD format.
        """
        if not isinstance(date_str, str):
            raise TypeError("Date must be a string in YYYY-MM-DD format.")

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc

        return date_str

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def id(self) -> str:
        return self._transaction_id

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def category(self) -> str:
        return self._category

    @property
    def description(self) -> str:
        return self._description

    @property
    def date(self) -> str:
        return self._date

    @property
    def type(self) -> str:
        return self.get_transaction_type()

    @abstractmethod
    def get_transaction_type(self) -> str:
        """
        Must be overridden by subclasses.
        """

    def to_dict(self) -> dict[str, str | float]:
        """
        Convert transaction object into dictionary format for saving/exporting.
        """
        return {
            "id": self.transaction_id,
            "type": self.get_transaction_type(),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    def __str__(self) -> str:
        return (
            f"{self.get_transaction_type().capitalize()} | "
            f"Amount: {self.amount:.2f} | "
            f"Category: {self.category} | "
            f"Description: {self.description} | "
            f"Date: {self.date}"
        )
