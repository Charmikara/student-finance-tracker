from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


class StudentFinanceCLI:
    def __init__(self) -> None:
        self.tracker = FinanceTracker()

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    self._add_income()
                elif choice == "2":
                    self._add_expense()
                elif choice == "3":
                    self._add_budget()
                elif choice == "4":
                    self._view_transactions()
                elif choice == "5":
                    self._view_report()
                elif choice == "6":
                    self._view_budget_status()
                elif choice == "7":
                    self._view_warnings()
                elif choice == "8":
                    self.tracker.save()
                    print("Data saved. Goodbye.")
                    break
                else:
                    print("Please choose a number from 1 to 8.")
            except (TypeError, ValueError) as error:
                print(f"Error: {error}")

    @staticmethod
    def _print_menu() -> None:
        print("\nStudent Finance Tracker")
        print("1. Add income")
        print("2. Add expense")
        print("3. Add budget")
        print("4. View transactions")
        print("5. View report")
        print("6. View budget status")
        print("7. View warnings")
        print("8. Save and exit")

    def _add_income(self) -> None:
        amount, category, description, date = self._get_transaction_input()
        self.tracker.add_income(amount, category, description, date)
        self.tracker.save()
        print("Income added and saved.")

    def _add_expense(self) -> None:
        amount, category, description, date = self._get_transaction_input()
        self.tracker.add_expense(amount, category, description, date)
        self.tracker.save()
        print("Expense added and saved.")

    def _add_budget(self) -> None:
        category = input("Category: ").strip()
        limit = float(input("Limit: ").strip())
        self.tracker.add_budget(category, limit)
        self.tracker.save()
        print("Budget added and saved.")

    def _view_transactions(self) -> None:
        print("\nTransactions:")
        if not self.tracker.transactions:
            print("No transactions found.")
            return

        for transaction in self.tracker.transactions:
            print(transaction)

    def _view_report(self) -> None:
        report = ReportGenerator().generate_report(self.tracker.transactions)

        print("\nReport summary:")
        print(f"Total income: {report['total_income']:.2f}")
        print(f"Total expenses: {report['total_expense']:.2f}")
        print(f"Balance: {report['balance']:.2f}")

        print("\nExpenses by category:")
        if not report["category_spending"]:
            print("No expenses found.")
            return

        for category, amount in report["category_spending"].items():
            print(f"{category}: {amount:.2f}")

    def _view_budget_status(self) -> None:
        print("\nBudget status:")
        status = self.tracker.get_budget_status()
        if not status:
            print("No budgets found.")
            return

        for category, details in status.items():
            print(
                f"{category}: spent {details['spent']:.2f} / "
                f"{details['limit']:.2f}, remaining {details['remaining']:.2f}"
            )

    def _view_warnings(self) -> None:
        warnings = WarningSystem().analyze(
            self.tracker.transactions,
            self.tracker.budgets,
            self.tracker.get_balance(),
        )

        print("\nWarnings:")
        if not warnings:
            print("No warnings.")
            return

        for warning in warnings:
            print(warning["message"])

    @staticmethod
    def _get_transaction_input() -> tuple[float, str, str, str]:
        amount = float(input("Amount: ").strip())
        category = input("Category: ").strip()
        description = input("Description: ").strip()
        date = input("Date (YYYY-MM-DD): ").strip()
        return amount, category, description, date


if __name__ == "__main__":
    StudentFinanceCLI().run()
