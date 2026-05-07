from utils.validators import normalize_category


class Budget:
    """
    Represents a spending budget for a specific category.
    """

    def __init__(self, category: str, limit: float) -> None:
        self._category = self._validate_category(category)
        self._limit = self._validate_limit(limit)

    @staticmethod
    def _validate_category(category: str) -> str:
        return normalize_category(category)

    @staticmethod
    def _validate_limit(limit: float) -> float:
        if not isinstance(limit, (int, float)):
            raise TypeError("Budget limit must be a number.")

        if limit <= 0:
            raise ValueError("Budget limit must be greater than 0.")

        return float(limit)

    @property
    def category(self) -> str:
        return self._category

    @property
    def limit(self) -> float:
        return self._limit

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "limit": self.limit
        }

    def __str__(self) -> str:
        return f"Budget | Category: {self.category} | Limit: {self.limit:.2f}"
