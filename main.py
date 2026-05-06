from services.finance_tracker import FinanceTracker


def main() -> None:
    tracker = FinanceTracker()

    tracker.add_income(500, "Allowance", "Monthly allowance", "2026-04-01")
    tracker.add_income(120, "Part-time Job", "Weekend work", "2026-04-05")

    tracker.add_expense(45, "Food", "Groceries", "2026-04-06")
    tracker.add_expense(12, "Transport", "Bus card top-up", "2026-04-07")
    tracker.add_expense(30, "Food", "Eating out", "2026-04-08")

    tracker.add_budget("Food", 70)
    tracker.add_budget("Transport", 25)

    print("Transactions:")
    for transaction in tracker.list_transactions():
        print(transaction)

    print("\nSummary:")
    print(f"Total income: {tracker.get_total_income():.2f}")
    print(f"Total expenses: {tracker.get_total_expenses():.2f}")
    print(f"Balance: {tracker.get_balance():.2f}")

    print("\nExpenses by category:")
    print(tracker.get_expenses_by_category())

    print("\nBudget status:")
    print(tracker.get_budget_status())


if __name__ == "__main__":
    main()