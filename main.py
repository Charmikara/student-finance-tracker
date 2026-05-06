from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


class StudentBudgetCLI:
    def __init__(self) -> None:
        self.tracker = FinanceTracker()
        self.report_generator = ReportGenerator()
        self.warning_system = WarningSystem()

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
                    self._set_budget()
                elif choice == "4":
                    self._list_transactions()
                elif choice == "5":
                    self._show_summary()
                elif choice == "6":
                    self._show_budget_status()
                elif choice == "7":
                    self._show_warnings()
                elif choice == "8":
                    self.tracker.save()
                    print("Saved. Goodbye.")
                    break
                else:
                    print("Invalid option.")
            except (TypeError, ValueError) as error:
                print(f"Error: {error}")

    @staticmethod
    def _print_menu() -> None:
        print("\nStudent Budget Tracker")
        print("1. Add income")
        print("2. Add expense")
        print("3. Set budget")
        print("4. List transactions")
        print("5. Show summary")
        print("6. Show budget status")
        print("7. Show warnings")
        print("8. Save and exit")

    def _add_income(self) -> None:
        amount, category, description, transaction_date = self._transaction_input()
        self.tracker.add_income(amount, category, description, transaction_date)
        self.tracker.save()
        print("Income added.")

    def _add_expense(self) -> None:
        amount, category, description, transaction_date = self._transaction_input()
        self.tracker.add_expense(amount, category, description, transaction_date)
        self.tracker.save()
        print("Expense added.")

    def _set_budget(self) -> None:
        category = input("Category: ").strip()
        limit = float(input("Limit: ").strip())
        self.tracker.add_budget(category, limit)
        self.tracker.save()
        print("Budget saved.")

    def _list_transactions(self) -> None:
        if not self.tracker.transactions:
            print("No transactions found.")
            return

        for transaction in self.tracker.transactions:
            print(transaction)

    def _show_summary(self) -> None:
        report = self.report_generator.generate_report(self.tracker.transactions)
        print(f"Income: {report['total_income']:.2f}")
        print(f"Expenses: {report['total_expense']:.2f}")
        print(f"Balance: {report['balance']:.2f}")

        if report["category_spending"]:
            print("Spending by category:")
            for category, amount in report["category_spending"].items():
                print(f"- {category}: {amount:.2f}")

    def _show_budget_status(self) -> None:
        status = self.tracker.get_budget_status()
        if not status:
            print("No budgets found.")
            return

        for category, details in status.items():
            print(
                f"{category}: spent {details['spent']:.2f} / "
                f"{details['limit']:.2f}, remaining {details['remaining']:.2f}"
            )

    def _show_warnings(self) -> None:
        warnings = self.warning_system.analyze(
            self.tracker.transactions,
            self.tracker.budgets,
            self.tracker.get_balance(),
        )

        if not warnings:
            print("No warnings.")
            return

        for warning in warnings:
            print(warning["message"])

    @staticmethod
    def _transaction_input() -> tuple[float, str, str, str]:
        amount = float(input("Amount: ").strip())
        category = input("Category: ").strip()
        description = input("Description: ").strip()
        transaction_date = input("Date (YYYY-MM-DD): ").strip()
        return amount, category, description, transaction_date


if __name__ == "__main__":
    StudentBudgetCLI().run()
