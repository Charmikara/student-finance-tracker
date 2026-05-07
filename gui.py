import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


class StudentFinanceGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Student Finance Tracker")
        self.tracker = FinanceTracker()

        self._build_form()
        self.transactions_text = self._create_text_area("Transactions", 7)
        self.report_text = self._create_text_area("Report", 6)
        self.budget_text = self._create_text_area("Budget Status", 6)
        self.warnings_text = self._create_text_area("Warnings", 5)

        self.refresh()

    def _build_form(self) -> None:
        form = tk.Frame(self.root, padx=10, pady=10)
        form.pack(fill="x")

        self.amount_entry = tk.Entry(form)
        self.category_entry = tk.Entry(form)
        self.description_entry = tk.Entry(form)
        self.date_entry = tk.Entry(form)

        self._add_labeled_entry(form, "Amount", self.amount_entry, 0)
        self._add_labeled_entry(form, "Category", self.category_entry, 1)
        self._add_labeled_entry(form, "Description", self.description_entry, 2)
        self._add_labeled_entry(form, "Date (YYYY-MM-DD)", self.date_entry, 3)

        buttons = tk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        tk.Button(buttons, text="Add Income", command=self.add_income).pack(side="left", padx=4)
        tk.Button(buttons, text="Add Expense", command=self.add_expense).pack(side="left", padx=4)
        tk.Button(buttons, text="Add Budget", command=self.add_budget).pack(side="left", padx=4)
        tk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left", padx=4)

    @staticmethod
    def _add_labeled_entry(parent: tk.Frame, label: str, entry: tk.Entry, row: int) -> None:
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        parent.columnconfigure(1, weight=1)

    def _create_text_area(self, title: str, height: int) -> ScrolledText:
        frame = tk.LabelFrame(self.root, text=title, padx=8, pady=6)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        text_area = ScrolledText(frame, height=height, wrap="word")
        text_area.pack(fill="both", expand=True)
        text_area.configure(state="disabled")
        return text_area

    def add_income(self) -> None:
        try:
            amount, category, description, date = self._get_transaction_input()
            self.tracker.add_income(amount, category, description, date)
            self.tracker.save()
            self._clear_inputs()
            self.refresh()
            messagebox.showinfo("Saved", "Income added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid input", str(error))

    def add_expense(self) -> None:
        try:
            amount, category, description, date = self._get_transaction_input()
            self.tracker.add_expense(amount, category, description, date)
            self.tracker.save()
            self._clear_inputs()
            self.refresh()
            messagebox.showinfo("Saved", "Expense added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid input", str(error))

    def add_budget(self) -> None:
        try:
            category = self._get_text(self.category_entry, "Category")
            limit = self._get_amount()
            self.tracker.add_budget(category, limit)
            self.tracker.save()
            self._clear_inputs()
            self.refresh()
            messagebox.showinfo("Saved", "Budget added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid input", str(error))

    def refresh(self) -> None:
        self._show_transactions()
        self._show_report()
        self._show_budget_status()
        self._show_warnings()

    def _show_transactions(self) -> None:
        lines = [str(transaction) for transaction in self.tracker.transactions]
        self._set_text(self.transactions_text, "\n".join(lines) or "No transactions found.")

    def _show_report(self) -> None:
        report = ReportGenerator().generate_report(self.tracker.transactions)
        lines = [
            f"Total income: {report['total_income']:.2f}",
            f"Total expenses: {report['total_expense']:.2f}",
            f"Balance: {report['balance']:.2f}",
            "",
            "Expenses by category:",
        ]

        if report["category_spending"]:
            for category, amount in report["category_spending"].items():
                lines.append(f"{category}: {amount:.2f}")
        else:
            lines.append("No expenses found.")

        self._set_text(self.report_text, "\n".join(lines))

    def _show_budget_status(self) -> None:
        status = self.tracker.get_budget_status()
        if not status:
            self._set_text(self.budget_text, "No budgets found.")
            return

        lines = []
        for category, details in status.items():
            state = "Exceeded" if details["exceeded"] else "OK"
            lines.append(
                f"{category}: spent {details['spent']:.2f}, "
                f"limit {details['limit']:.2f}, "
                f"remaining {details['remaining']:.2f} ({state})"
            )

        self._set_text(self.budget_text, "\n".join(lines))

    def _show_warnings(self) -> None:
        warnings = WarningSystem().analyze(
            self.tracker.transactions,
            self.tracker.budgets,
            self.tracker.get_balance(),
        )
        lines = [warning["message"] for warning in warnings]
        self._set_text(self.warnings_text, "\n".join(lines) or "No warnings.")

    def _get_transaction_input(self) -> tuple[float, str, str, str]:
        amount = self._get_amount()
        category = self._get_text(self.category_entry, "Category")
        description = self._get_text(self.description_entry, "Description")
        date = self._get_text(self.date_entry, "Date")
        return amount, category, description, date

    def _get_amount(self) -> float:
        value = self._get_text(self.amount_entry, "Amount")
        amount = float(value)
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        return amount

    @staticmethod
    def _get_text(entry: tk.Entry, field_name: str) -> str:
        value = entry.get().strip()
        if not value:
            raise ValueError(f"{field_name} cannot be empty.")
        return value

    @staticmethod
    def _set_text(text_area: ScrolledText, content: str) -> None:
        text_area.configure(state="normal")
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, content)
        text_area.configure(state="disabled")

    def _clear_inputs(self) -> None:
        for entry in (
            self.amount_entry,
            self.category_entry,
            self.description_entry,
            self.date_entry,
        ):
            entry.delete(0, tk.END)


def main() -> None:
    root = tk.Tk()
    StudentFinanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
