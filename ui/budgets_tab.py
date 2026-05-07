import tkinter as tk
from tkinter import messagebox, ttk

from services.warning_system import WarningSystem
from ui.constants import COMMON_CATEGORIES


class BudgetsTab:
    def __init__(self, parent: ttk.Frame, app) -> None:
        self.parent = parent
        self.app = app

        self._build()

    def _build(self) -> None:
        form = ttk.LabelFrame(self.parent, text="Add Budget", padding=10)
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
            self.parent,
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

        warnings_frame = ttk.LabelFrame(self.parent, text="Warnings", padding=10)
        warnings_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.warnings_list = tk.Listbox(warnings_frame, height=6)
        self.warnings_list.pack(fill="both", expand=True)

    def refresh(self) -> None:
        self.budget_tree.delete(*self.budget_tree.get_children())

        for category, details in self.app.tracker.get_budget_status().items():
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
            self.app.tracker.transactions,
            self.app.tracker.budgets,
            self.app.tracker.get_balance(),
        )
        if not warnings:
            self.warnings_list.insert(tk.END, "- No warnings.")
            return

        for warning in warnings:
            self.warnings_list.insert(tk.END, f"- {warning['message']}")

    def _add_budget(self) -> None:
        try:
            category = self._get_required_text(
                self.budget_category_var.get(),
                "Budget category",
            )
            limit = self._get_positive_float(self.budget_limit_var.get(), "Budget limit")
            self.app.tracker.add_budget(category, limit)
            self.app.tracker.save()
            self.budget_category_var.set("")
            self.budget_limit_var.set("")
            self.app.refresh()
            self.app.set_status("Budget added and saved.")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Invalid budget", str(error))

    def _delete_selected_budget(self) -> None:
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showerror("Delete budget", "Please select a budget to delete.")
            return

        try:
            self.app.tracker.delete_budget(selection[0])
            self.app.tracker.save()
            self.app.refresh()
            self.app.set_status("Budget deleted and saved.")
        except (KeyError, ValueError) as error:
            messagebox.showerror("Delete budget", str(error))

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
