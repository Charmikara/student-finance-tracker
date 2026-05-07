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
        self.status_var = tk.StringVar(value="Ready")

        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self.root, padding=(10, 8))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Load Sample Data", command=self.load_sample_data).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Clear All Data", command=self.clear_all_data).pack(side="left", padx=4)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.dashboard_tab = ttk.Frame(notebook, padding=10)
        self.transactions_tab = ttk.Frame(notebook, padding=10)
        self.budgets_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.budgets_tab, text="Budgets & Warnings")

        self._build_dashboard_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            padding=(10, 5),
            relief="sunken",
        )
        status_bar.pack(fill="x")

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
        ttk.Button(buttons, text="Delete Selected Transaction", command=self.delete_selected_transaction).pack(side="left", padx=4)

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
        self.transactions_tree.tag_configure("income", background="#edf7ed")
        self.transactions_tree.tag_configure("expense", background="#fff1f1")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.transactions_tree.yview,
        )
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_budgets_tab(self) -> None:
        form = ttk.LabelFrame(self.budgets_tab, text="Add Budget", padding=10)
        form.pack(fill="x", pady=(0, 10))

        self.budget_category_entry = ttk.Entry(form)
        self.budget_limit_entry = ttk.Entry(form)

        self._add_labeled_entry(form, "Category", self.budget_category_entry, 0)
        self._add_labeled_entry(form, "Limit", self.budget_limit_entry, 1)

        budget_buttons = ttk.Frame(form)
        budget_buttons.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(budget_buttons, text="Add Budget", command=self.add_budget).pack(side="left", padx=4)
        ttk.Button(budget_buttons, text="Delete Selected Budget", command=self.delete_selected_budget).pack(side="left", padx=4)

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
        self.budget_tree.tag_configure("exceeded", background="#fff1f1")

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
            self._set_status("Income added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid input", str(error))

    def add_expense(self) -> None:
        try:
            amount, category, description, date = self._get_transaction_input()
            self.tracker.add_expense(amount, category, description, date)
            self.tracker.save()
            self._clear_inputs()
            self.refresh()
            self._set_status("Expense added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid input", str(error))

    def add_budget(self) -> None:
        try:
            category = self._get_text(self.budget_category_entry, "Budget category")
            limit = self._get_positive_number(self.budget_limit_entry, "Budget limit")
            self.tracker.add_budget(category, limit)
            self.tracker.save()
            self._clear_budget_inputs()
            self.refresh()
            self._set_status("Budget added and saved.")
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
            self._set_status("Sample data loaded.")
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
        self._set_status("All data cleared.")

    def delete_selected_transaction(self) -> None:
        selected = self.transactions_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a transaction to delete.")
            return

        index = int(selected[0])
        try:
            self.tracker.delete_transaction_by_index(index)
            self.tracker.save()
            self.refresh()
            self._set_status("Transaction deleted and saved.")
        except (IndexError, TypeError, ValueError) as error:
            messagebox.showerror("Could not delete transaction", str(error))

    def delete_selected_budget(self) -> None:
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a budget to delete.")
            return

        category = selected[0]
        try:
            self.tracker.delete_budget(category)
            self.tracker.save()
            self.refresh()
            self._set_status("Budget deleted and saved.")
        except (KeyError, TypeError, ValueError) as error:
            messagebox.showerror("Could not delete budget", str(error))

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

        total_expenses = sum(category_spending.values())
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
                text=f"{amount:.2f} ({(amount / total_expenses) * 100:.1f}%)",
            )

    def _show_transactions(self) -> None:
        self.transactions_tree.delete(*self.transactions_tree.get_children())
        for index, transaction in enumerate(self.tracker.transactions):
            transaction_type = transaction.get_transaction_type()
            self.transactions_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    transaction_type,
                    f"{transaction.amount:.2f}",
                    transaction.category,
                    transaction.description,
                    transaction.date,
                ),
                tags=(transaction_type,),
            )

    def _show_budget_status(self) -> None:
        self.budget_tree.delete(*self.budget_tree.get_children())
        for category, details in self.tracker.get_budget_status().items():
            status = "Exceeded" if details["exceeded"] else "OK"
            self.budget_tree.insert(
                "",
                tk.END,
                iid=category,
                values=(
                    category,
                    f"{details['spent']:.2f}",
                    f"{details['limit']:.2f}",
                    f"{details['remaining']:.2f}",
                    status,
                ),
                tags=("exceeded",) if details["exceeded"] else (),
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
        return self._get_positive_number(self.amount_entry, "Amount")

    def _get_positive_number(self, entry: ttk.Entry, field_name: str) -> float:
        value = self._get_text(entry, field_name)
        try:
            amount = float(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid number.") from exc
        if amount <= 0:
            raise ValueError(f"{field_name} must be greater than 0.")
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

    def _clear_budget_inputs(self) -> None:
        self.budget_category_entry.delete(0, tk.END)
        self.budget_limit_entry.delete(0, tk.END)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)


def main() -> None:
    root = tk.Tk()
    StudentFinanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
