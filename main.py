from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


def print_transactions(tracker: FinanceTracker) -> None:
    print("Transactions:")
    for transaction in tracker.list_transactions():
        print(transaction)


def print_report(report: dict) -> None:
    print("\nReport summary:")
    print(f"Total income: {report['total_income']:.2f}")
    print(f"Total expenses: {report['total_expense']:.2f}")
    print(f"Balance: {report['balance']:.2f}")


def print_category_spending(report: dict) -> None:
    print("\nExpenses by category:")
    for category, amount in report["category_spending"].items():
        print(f"{category}: {amount:.2f}")


def print_budget_status(tracker: FinanceTracker) -> None:
    print("\nBudget status:")
    for category, details in tracker.get_budget_status().items():
        print(
            f"{category}: spent {details['spent']:.2f} / "
            f"{details['limit']:.2f}, remaining {details['remaining']:.2f}"
        )


def print_warnings(warnings: list) -> None:
    print("\nWarnings:")
    if not warnings:
        print("No warnings.")
        return

    for warning in warnings:
        print(warning["message"])


def main() -> None:
    tracker = FinanceTracker()

    tracker.add_income(500, "Allowance", "Monthly allowance", "2026-04-01")
    tracker.add_income(120, "Part-time Job", "Weekend work", "2026-04-05")

    tracker.add_expense(45, "Food", "Groceries", "2026-04-06")
    tracker.add_expense(12, "Transport", "Bus card top-up", "2026-04-07")
    tracker.add_expense(30, "Food", "Eating out", "2026-04-08")

    tracker.add_budget("Food", 70)
    tracker.add_budget("Transport", 25)

    report_generator = ReportGenerator()
    report = report_generator.generate_report(tracker.transactions)

    warning_system = WarningSystem()
    warnings = warning_system.analyze(
        tracker.transactions,
        tracker.budgets,
        tracker.get_balance(),
    )

    print_transactions(tracker)
    print_report(report)
    print_category_spending(report)
    print_budget_status(tracker)
    print_warnings(warnings)

    tracker.save()
    print("\nData saved successfully.")


if __name__ == "__main__":
    main()
