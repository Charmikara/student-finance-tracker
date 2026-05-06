from abc import ABC
from datetime import datetime
from typing import Dict


class Transaction(ABC):
    """
    Base class for all financial transactions.
    Stores: amount, category, description, date, etc
    """

    def __init__(self, amount: float, category: str, description: str, date: str) -> None:
        self._amount = self._validate_amount(amount)
        self._category = self._validate_text_field(category, "category")
        self._description = self._validate_text_field(description, "description")
        self._date = self._validate_date(date)

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

    def get_transaction_type(self) -> str:
        """
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must define the transaction type.")

    def to_dict(self) -> Dict[str, str | float]:
        """
        Convert transaction object into dictionary format for saving/exporting.
        """
        return {
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
