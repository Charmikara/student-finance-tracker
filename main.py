from models.expense import Expense
from models.income import Income


def main() -> None:
    expense1 = Expense(-10, "Food", "Lunch", "2026-04-17")
    income1 = Income(500.00, "Allowance", "Monthly allowance from parents", "2026-04-01")

    print(expense1)
    print(income1)

    print("\nDictionary output:")
    print(expense1.to_dict())
    print(income1.to_dict())


if __name__ == "__main__":
    main()