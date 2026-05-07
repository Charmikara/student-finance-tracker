import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem


COMMON_CATEGORIES = [
    "food",
    "transport",
    "rent",
    "groceries",
    "study",
    "entertainment",
    "health",
    "salary",
    "allowance",
    "other",
]


class StudentFinanceGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Student Finance Tracker")
        self.root.geometry("980x680")

        self.tracker = FinanceTracker()
        self.status_text = tk.StringVar(value="Ready")

        self._build_toolbar()
        self._build_tabs()
        self._build_status_bar()
        self.refresh()

    def _build_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, padding=(12, 10))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(
            toolbar,
            text="Load Sample Data",
            command=self._load_sample_data,
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            toolbar,
            text="Reset All Data",
            command=self._reset_all_data,
        ).pack(side="left", padx=(8, 0))

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.transactions_tab = ttk.Frame(self.notebook, padding=12)
        self.budgets_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.budgets_tab, text="Budgets & Warnings")

        self._build_dashboard_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()

    def _build_status_bar(self) -> None:
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_text,
            anchor="w",
            padding=(12, 6),
        )
        status_bar.pack(fill="x", side="bottom")

    def _build_dashboard_tab(self) -> None:
        overview = ttk.LabelFrame(self.dashboard_tab, text="Overview", padding=10)
        overview.pack(fill="x")

        self.card_values: dict[str, tk.StringVar] = {}
        labels = [
            ("total_income", "Total income"),
            ("total_expense", "Total expenses"),
            ("balance", "Balance"),
            ("transaction_count", "Transactions"),
            ("budget_count", "Budgets"),
            ("exceeded_count", "Exceeded budgets"),
            ("top_category", "Top category"),
        ]

        for index, (key, label) in enumerate(labels):
            card = ttk.Frame(overview, padding=8)
            card.grid(row=index // 4, column=index % 4, sticky="ew", padx=4, pady=4)
            overview.columnconfigure(index % 4, weight=1)

            self.card_values[key] = tk.StringVar(value="-")
            ttk.Label(card, text=label).pack(anchor="w")
            ttk.Label(
                card,
                textvariable=self.card_values[key],
                font=("TkDefaultFont", 12, "bold"),
            ).pack(anchor="w", pady=(4, 0))

        chart_frame = ttk.LabelFrame(
            self.dashboard_tab,
            text="Spending by Category",
            padding=10,
        )
        chart_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.chart_canvas = tk.Canvas(chart_frame, height=260, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)

    def _build_transactions_tab(self) -> None:
        form = ttk.LabelFrame(
            self.transactions_tab,
            text="Add Transaction",
            padding=10,
        )
        form.pack(fill="x")

        self.transaction_type_var = tk.StringVar(value="expense")
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.date_var = tk.StringVar(value=date.today().isoformat())

        fields = [
            ("Type", ttk.Combobox(
                form,
                textvariable=self.transaction_type_var,
                values=["income", "expense"],
                state="readonly",
            )),
            ("Amount", ttk.Entry(form, textvariable=self.amount_var)),
            ("Category", ttk.Combobox(
                form,
                textvariable=self.category_var,
                values=COMMON_CATEGORIES,
            )),
            ("Description", ttk.Entry(form, textvariable=self.description_var)),
            ("Date", ttk.Entry(form, textvariable=self.date_var)),
        ]

        for column, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=column, sticky="w")
            widget.grid(row=1, column=column, sticky="ew", padx=(0, 8), pady=(3, 0))
            form.columnconfigure(column, weight=1)

        ttk.Label(form, text="EUR").grid(row=1, column=5, sticky="w")

        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=6, sticky="w", pady=(10, 0))
        ttk.Button(
            buttons,
            text="Add Transaction",
            command=self._add_transaction,
        ).pack(side="left")
        ttk.Button(
            buttons,
            text="Delete Selected Transaction",
            command=self._delete_selected_transaction,
        ).pack(side="left", padx=(8, 0))

        table_frame = ttk.LabelFrame(
            self.transactions_tab,
            text="Transactions",
            padding=10,
        )
        table_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("type", "amount", "category", "description", "date")
        self.transactions_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        headings = {
            "type": "Type",
            "amount": "Amount",
            "category": "Category",
            "description": "Description",
            "date": "Date",
        }
        for column, heading in headings.items():
            self.transactions_tree.heading(column, text=heading)
            self.transactions_tree.column(column, width=150, anchor="w")

        self.transactions_tree.tag_configure("income", background="#eaf7ea")
        self.transactions_tree.tag_configure("expense", background="#fff0f0")
        self.transactions_tree.pack(fill="both", expand=True)

    def _build_budgets_tab(self) -> None:
        form = ttk.LabelFrame(self.budgets_tab, text="Add Budget", padding=10)
        form.pack(fill="x")

        self.budget_category_var = tk.StringVar()
        self.budget_limit_var = tk.StringVar()

        ttk.Label(form, text="Category").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Limit").grid(row=0, column=1, sticky="w")

        ttk.Combobox(
            form,
            textvariable=self.budget_category_var,
            values=COMMON_CATEGORIES,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Entry(form, textvariable=self.budget_limit_var).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 8),
        )
        ttk.Label(form, text="EUR").grid(row=1, column=2, sticky="w")
        ttk.Button(form, text="Add Budget", command=self._add_budget).grid(
            row=1,
            column=3,
            padx=(8, 0),
        )
        ttk.Button(
            form,
            text="Delete Selected Budget",
            command=self._delete_selected_budget,
        ).grid(row=1, column=4, padx=(8, 0))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        budget_frame = ttk.LabelFrame(
            self.budgets_tab,
            text="Budget Status",
            padding=10,
        )
        budget_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("category", "spent", "limit", "remaining", "status")
        self.budget_tree = ttk.Treeview(
            budget_frame,
            columns=columns,
            show="headings",
            height=8,
        )
        for column in columns:
            self.budget_tree.heading(column, text=column.capitalize())
            self.budget_tree.column(column, width=140, anchor="w")
        self.budget_tree.tag_configure("exceeded", background="#ffe5e5")
        self.budget_tree.pack(fill="both", expand=True)

        warnings_frame = ttk.LabelFrame(self.budgets_tab, text="Warnings", padding=10)
        warnings_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.warnings_list = tk.Listbox(warnings_frame, height=6)
        self.warnings_list.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self._refresh_dashboard()
        self._refresh_transactions()
        self._refresh_budgets_and_warnings()
        self._set_status("Ready")

    def _refresh_dashboard(self) -> None:
        report = ReportGenerator().generate_report(self.tracker.transactions)
        budget_status = self.tracker.get_budget_status()
        category_spending = report["category_spending"]
        exceeded_count = sum(
            1 for details in budget_status.values()
            if details["exceeded"]
        )
        top_category = "None"
        if category_spending:
            top_category = max(category_spending, key=category_spending.get)

        self.card_values["total_income"].set(f"{report['total_income']:.2f} EUR")
        self.card_values["total_expense"].set(f"{report['total_expense']:.2f} EUR")
        self.card_values["balance"].set(f"{report['balance']:.2f} EUR")
        self.card_values["transaction_count"].set(str(len(self.tracker.transactions)))
        self.card_values["budget_count"].set(str(len(self.tracker.budgets)))
        self.card_values["exceeded_count"].set(str(exceeded_count))
        self.card_values["top_category"].set(top_category)

        self._draw_spending_chart(category_spending)

    def _draw_spending_chart(self, category_spending: dict[str, float]) -> None:
        canvas = self.chart_canvas
        canvas.delete("all")

        if not category_spending:
            canvas.create_text(
                20,
                40,
                anchor="w",
                text="No expense categories yet. Add an expense or load sample data.",
                fill="#555555",
            )
            return

        width = max(canvas.winfo_width(), 700)
        max_amount = max(category_spending.values())
        total = sum(category_spending.values())
        y = 25

        for category, amount in sorted(category_spending.items()):
            percentage = (amount / total) * 100 if total else 0
            bar_width = int((width - 260) * (amount / max_amount))

            canvas.create_text(
                10,
                y + 10,
                anchor="w",
                text=f"{category} - {amount:.2f} EUR ({percentage:.1f}%)",
            )
            canvas.create_rectangle(220, y, 220 + bar_width, y + 20, fill="#4a90e2")
            y += 38

    def _refresh_transactions(self) -> None:
        self.transactions_tree.delete(*self.transactions_tree.get_children())

        for index, transaction in enumerate(self.tracker.transactions):
            transaction_type = transaction.get_transaction_type()
            self.transactions_tree.insert(
                "",
                "end",
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

    def _refresh_budgets_and_warnings(self) -> None:
        self.budget_tree.delete(*self.budget_tree.get_children())

        for category, details in self.tracker.get_budget_status().items():
            status = "Exceeded" if details["exceeded"] else "OK"
            tags = ("exceeded",) if details["exceeded"] else ()
            self.budget_tree.insert(
                "",
                "end",
                iid=category,
                values=(
                    category,
                    f"{details['spent']:.2f}",
                    f"{details['limit']:.2f}",
                    f"{details['remaining']:.2f}",
                    status,
                ),
                tags=tags,
            )

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

    def _add_transaction(self) -> None:
        try:
            amount = self._get_positive_float(self.amount_var.get(), "Amount")
            category = self._get_required_text(self.category_var.get(), "Category")
            description = self._get_required_text(
                self.description_var.get(),
                "Description",
            )
            transaction_date = self._get_valid_date(self.date_var.get())

            if self.transaction_type_var.get() == "income":
                self.tracker.add_income(amount, category, description, transaction_date)
                message = "Income added and saved."
            else:
                self.tracker.add_expense(amount, category, description, transaction_date)
                message = "Expense added and saved."

            self.tracker.save()
            self._clear_transaction_form()
            self.refresh()
            self._set_status(message)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid transaction", str(error))

    def _add_budget(self) -> None:
        try:
            category = self._get_required_text(
                self.budget_category_var.get(),
                "Budget category",
            )
            limit = self._get_positive_float(self.budget_limit_var.get(), "Budget limit")
            self.tracker.add_budget(category, limit)
            self.tracker.save()
            self.budget_category_var.set("")
            self.budget_limit_var.set("")
            self.refresh()
            self._set_status("Budget added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid budget", str(error))

    def _delete_selected_transaction(self) -> None:
        try:
            index = self._selected_transaction_index()
            self.tracker.delete_transaction_by_index(index)
            self.tracker.save()
            self.refresh()
            self._set_status("Transaction deleted and saved.")
        except (IndexError, TypeError, ValueError) as error:
            messagebox.showerror("Delete transaction", str(error))

    def _delete_selected_budget(self) -> None:
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showerror("Delete budget", "Please select a budget to delete.")
            return

        try:
            self.tracker.delete_budget(selection[0])
            self.tracker.save()
            self.refresh()
            self._set_status("Budget deleted and saved.")
        except (KeyError, ValueError) as error:
            messagebox.showerror("Delete budget", str(error))

    def _load_sample_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Load sample data",
            "This will create a backup, then replace current transactions and "
            "budgets with sample data. Continue?",
        )
        if not confirmed:
            return

        try:
            self.tracker.backup_current_data()
            self.tracker.load_sample_data()
            self.tracker.save()
            self.refresh()
            self._set_status("Backup checked. Sample data loaded.")
        except (OSError, ValueError) as error:
            messagebox.showerror("Load sample data", str(error))

    def _reset_all_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Reset all data",
            "This will create a backup, then delete all current transactions and "
            "budgets. Continue?",
        )
        if not confirmed:
            return

        try:
            self.tracker.backup_current_data()
            self.tracker.clear_data()
            self.tracker.save()
            self.refresh()
            self._set_status("Backup checked. All data reset.")
        except OSError as error:
            messagebox.showerror("Reset all data", str(error))

    def _selected_transaction_index(self) -> int:
        selection = self.transactions_tree.selection()
        if not selection:
            raise ValueError("Please select a transaction to delete.")
        return int(selection[0])

    def _clear_transaction_form(self) -> None:
        self.amount_var.set("")
        self.category_var.set("")
        self.description_var.set("")
        self.date_var.set(date.today().isoformat())

    def _set_status(self, message: str) -> None:
        self.status_text.set(message)

    @staticmethod
    def _get_positive_float(value: str, field_name: str) -> float:
        try:
            number = float(value.strip())
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid number.") from exc

        if number <= 0:
            raise ValueError(f"{field_name} must be greater than 0.")

        return number

    @staticmethod
    def _get_required_text(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty.")
        return cleaned_value

    @staticmethod
    def _get_valid_date(value: str) -> str:
        cleaned_value = value.strip()
        try:
            date.fromisoformat(cleaned_value)
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc
        return cleaned_value


if __name__ == "__main__":
    root_window = tk.Tk()
    app = StudentFinanceGUI(root_window)
    root_window.mainloop()
