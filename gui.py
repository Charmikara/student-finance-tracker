from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


class StudentFinanceGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Student Finance Tracker")
        self.root.geometry("980x720")
        self.tracker = FinanceTracker()

        self.metric_labels = {}

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_tab = ttk.Frame(notebook, padding=10)
        self.transactions_tab = ttk.Frame(notebook, padding=10)
        self.budgets_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.budgets_tab, text="Budgets & Warnings")

        self._build_dashboard_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()

    def _build_dashboard_tab(self) -> None:
        overview = ttk.LabelFrame(self.dashboard_tab, text="Overview", padding=10)
        overview.pack(fill="x", pady=(0, 10))

        metrics = [
            ("total_income", "Total Income"),
            ("total_expenses", "Total Expenses"),
            ("balance", "Balance"),
            ("transactions", "Transactions"),
            ("budgets", "Budgets"),
            ("exceeded_budgets", "Exceeded Budgets"),
            ("top_category", "Top Spending Category"),
        ]

        for index, (key, title) in enumerate(metrics):
            card = ttk.Frame(overview, padding=10, relief="ridge")
            card.grid(row=index // 4, column=index % 4, sticky="nsew", padx=5, pady=5)
            ttk.Label(card, text=title).pack(anchor="w")
            value_label = ttk.Label(card, text="-", font=("TkDefaultFont", 11, "bold"))
            value_label.pack(anchor="w", pady=(6, 0))
            self.metric_labels[key] = value_label

        for column in range(4):
            overview.columnconfigure(column, weight=1)

        chart_frame = ttk.LabelFrame(
            self.dashboard_tab,
            text="Spending by Category",
            padding=10,
        )
        chart_frame.pack(fill="both", expand=True)
        self.spending_canvas = tk.Canvas(chart_frame, height=260, bg="white")
        self.spending_canvas.pack(fill="both", expand=True)

    def _build_transactions_tab(self) -> None:
        form = ttk.LabelFrame(self.transactions_tab, text="Add Entry", padding=10)
        form.pack(fill="x", pady=(0, 10))

        self.amount_entry = ttk.Entry(form)
        self.category_entry = ttk.Entry(form)
        self.description_entry = ttk.Entry(form)
        self.date_entry = ttk.Entry(form)

        self._add_labeled_entry(form, "Amount", self.amount_entry, 0)
        self._add_labeled_entry(form, "Category", self.category_entry, 1)
        self._add_labeled_entry(form, "Description", self.description_entry, 2)
        self._add_labeled_entry(form, "Date (YYYY-MM-DD)", self.date_entry, 3)

        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(buttons, text="Add Income", command=self.add_income).pack(side="left", padx=4)
        ttk.Button(buttons, text="Add Expense", command=self.add_expense).pack(side="left", padx=4)
        ttk.Button(buttons, text="Add Budget", command=self.add_budget).pack(side="left", padx=4)
        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(buttons, text="Load Sample Data", command=self.load_sample_data).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear All Data", command=self.clear_all_data).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(
            self.transactions_tab,
            text="Transactions",
            padding=10,
        )
        table_frame.pack(fill="both", expand=True)

        columns = ("type", "amount", "category", "description", "date")
        self.transactions_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=14,
        )
        headings = {
            "type": "Type",
            "amount": "Amount",
            "category": "Category",
            "description": "Description",
            "date": "Date",
        }
        widths = {
            "type": 90,
            "amount": 90,
            "category": 130,
            "description": 320,
            "date": 120,
        }
        for column in columns:
            self.transactions_tree.heading(column, text=headings[column])
            self.transactions_tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.transactions_tree.yview,
        )
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_budgets_tab(self) -> None:
        budget_frame = ttk.LabelFrame(
            self.budgets_tab,
            text="Budget Status",
            padding=10,
        )
        budget_frame.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("category", "spent", "limit", "remaining", "status")
        self.budget_tree = ttk.Treeview(
            budget_frame,
            columns=columns,
            show="headings",
            height=10,
        )
        headings = {
            "category": "Category",
            "spent": "Spent",
            "limit": "Limit",
            "remaining": "Remaining",
            "status": "Status",
        }
        for column in columns:
            self.budget_tree.heading(column, text=headings[column])
            self.budget_tree.column(column, width=140, anchor="w")

        self.budget_tree.pack(fill="both", expand=True)

        warnings_frame = ttk.LabelFrame(
            self.budgets_tab,
            text="Warnings",
            padding=10,
        )
        warnings_frame.pack(fill="both", expand=True)

        self.warnings_list = tk.Listbox(warnings_frame, height=8)
        self.warnings_list.pack(fill="both", expand=True)

    @staticmethod
    def _add_labeled_entry(parent: ttk.Frame, label: str, entry: ttk.Entry, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        parent.columnconfigure(1, weight=1)

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
        self._show_dashboard()
        self._show_transactions()
        self._show_budget_status()
        self._show_warnings()

    def load_sample_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Load Sample Data",
            "This will replace current transactions and budgets with sample data. Continue?",
        )
        if not confirmed:
            return

        try:
            self.tracker.load_sample_data()
            self.tracker.save()
            self.refresh()
            messagebox.showinfo("Sample Data Loaded", "Sample data loaded and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Could not load sample data", str(error))

    def clear_all_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Clear All Data",
            "This will delete all current transactions and budgets. Continue?",
        )
        if not confirmed:
            return

        self.tracker.clear_data()
        self.tracker.save()
        self.refresh()
        messagebox.showinfo("Data Cleared", "All data cleared and saved.")

    def _show_dashboard(self) -> None:
        report = ReportGenerator().generate_report(self.tracker.transactions)
        budget_status = self.tracker.get_budget_status()
        exceeded_count = sum(
            1 for details in budget_status.values()
            if details["exceeded"]
        )
        top_category = self._get_top_spending_category(report["category_spending"])

        values = {
            "total_income": f"{report['total_income']:.2f}",
            "total_expenses": f"{report['total_expense']:.2f}",
            "balance": f"{report['balance']:.2f}",
            "transactions": str(len(self.tracker.transactions)),
            "budgets": str(len(self.tracker.budgets)),
            "exceeded_budgets": str(exceeded_count),
            "top_category": top_category or "None",
        }
        for key, value in values.items():
            self.metric_labels[key].configure(text=value)

        self._draw_spending_chart(report["category_spending"])

    def _draw_spending_chart(self, category_spending: dict) -> None:
        canvas = self.spending_canvas
        canvas.delete("all")

        if not category_spending:
            canvas.create_text(20, 20, anchor="w", text="No expenses found.")
            return

        max_amount = max(category_spending.values())
        left_margin = 150
        bar_height = 24
        gap = 14
        max_bar_width = 650

        for index, (category, amount) in enumerate(category_spending.items()):
            y = 20 + index * (bar_height + gap)
            width = (amount / max_amount) * max_bar_width if max_amount else 0
            canvas.create_text(10, y + 12, anchor="w", text=category)
            canvas.create_rectangle(
                left_margin,
                y,
                left_margin + width,
                y + bar_height,
                fill="#4f81bd",
                outline="",
            )
            canvas.create_text(
                left_margin + width + 8,
                y + 12,
                anchor="w",
                text=f"{amount:.2f}",
            )

    def _show_transactions(self) -> None:
        self.transactions_tree.delete(*self.transactions_tree.get_children())
        for transaction in self.tracker.transactions:
            self.transactions_tree.insert(
                "",
                tk.END,
                values=(
                    transaction.get_transaction_type(),
                    f"{transaction.amount:.2f}",
                    transaction.category,
                    transaction.description,
                    transaction.date,
                ),
            )

    def _show_budget_status(self) -> None:
        self.budget_tree.delete(*self.budget_tree.get_children())
        for category, details in self.tracker.get_budget_status().items():
            status = "Exceeded" if details["exceeded"] else "OK"
            self.budget_tree.insert(
                "",
                tk.END,
                values=(
                    category,
                    f"{details['spent']:.2f}",
                    f"{details['limit']:.2f}",
                    f"{details['remaining']:.2f}",
                    status,
                ),
            )

    def _show_warnings(self) -> None:
        self.warnings_list.delete(0, tk.END)
        warnings = WarningSystem().analyze(
            self.tracker.transactions,
            self.tracker.budgets,
            self.tracker.get_balance(),
        )
        if not warnings:
            self.warnings_list.insert(tk.END, "- No warnings.")
            return

        for warning in warnings:
            self.warnings_list.insert(tk.END, f"- {warning['message']}")

    @staticmethod
    def _get_top_spending_category(category_spending: dict) -> str | None:
        if not category_spending:
            return None

        category, amount = max(category_spending.items(), key=lambda item: item[1])
        return f"{category} ({amount:.2f})"

    def _get_transaction_input(self) -> tuple[float, str, str, str]:
        amount = self._get_amount()
        category = self._get_text(self.category_entry, "Category")
        description = self._get_text(self.description_entry, "Description")
        date = self._get_valid_date()
        return amount, category, description, date

    def _get_valid_date(self) -> str:
        date_text = self._get_text(self.date_entry, "Date")
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc
        return date_text

    def _get_amount(self) -> float:
        value = self._get_text(self.amount_entry, "Amount")
        try:
            amount = float(value)
        except ValueError as exc:
            raise ValueError("Amount must be a valid number.") from exc
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        return amount

    @staticmethod
    def _get_text(entry: ttk.Entry, field_name: str) -> str:
        value = entry.get().strip()
        if not value:
            raise ValueError(f"{field_name} cannot be empty.")
        return value

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
