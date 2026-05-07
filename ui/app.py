import tkinter as tk
from tkinter import messagebox, ttk

from services.finance_tracker import FinanceTracker
from ui.budgets_tab import BudgetsTab
from ui.dashboard_tab import DashboardTab
from ui.transactions_tab import TransactionsTab


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

        dashboard_frame = ttk.Frame(self.notebook, padding=12)
        transactions_frame = ttk.Frame(self.notebook, padding=12)
        budgets_frame = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(dashboard_frame, text="Dashboard")
        self.notebook.add(transactions_frame, text="Transactions")
        self.notebook.add(budgets_frame, text="Budgets & Warnings")

        self.dashboard_tab = DashboardTab(dashboard_frame, self)
        self.transactions_tab = TransactionsTab(transactions_frame, self)
        self.budgets_tab = BudgetsTab(budgets_frame, self)

    def _build_status_bar(self) -> None:
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_text,
            anchor="w",
            padding=(12, 6),
        )
        status_bar.pack(fill="x", side="bottom")

    def refresh(self) -> None:
        self.dashboard_tab.refresh()
        self.transactions_tab.refresh()
        self.budgets_tab.refresh()
        self.set_status("Ready")

    def set_status(self, message: str) -> None:
        self.status_text.set(message)

    def _load_sample_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Load sample data",
            "This will replace current transactions and budgets with sample data. "
            "If existing data is found, a backup will be created first. Continue?",
        )
        if not confirmed:
            return

        try:
            backups = self.tracker.backup_current_data()
            self.tracker.load_sample_data()
            self.tracker.save()
            self.refresh()
            if backups:
                self.set_status("Backup created. Sample data loaded.")
            else:
                self.set_status("No existing data found. Sample data loaded.")
        except (OSError, ValueError) as error:
            messagebox.showerror("Load sample data", str(error))

    def _reset_all_data(self) -> None:
        confirmed = messagebox.askyesno(
            "Reset all data",
            "This will delete all current transactions and budgets. "
            "If existing data is found, a backup will be created first. Continue?",
        )
        if not confirmed:
            return

        try:
            backups = self.tracker.backup_current_data()
            self.tracker.clear_data()
            self.tracker.save()
            self.refresh()
            if backups:
                self.set_status("Backup created. All data reset.")
            else:
                self.set_status("No existing data found. All data reset.")
        except OSError as error:
            messagebox.showerror("Reset all data", str(error))
