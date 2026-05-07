import tkinter as tk
from tkinter import ttk

from services.report_generator import ReportGenerator


class DashboardTab:
    def __init__(self, parent: ttk.Frame, app) -> None:
        self.parent = parent
        self.app = app
        self.card_values: dict[str, tk.StringVar] = {}

        self._build()

    def _build(self) -> None:
        overview = ttk.LabelFrame(self.parent, text="Overview", padding=10)
        overview.pack(fill="x")

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
            self.parent,
            text="Spending by Category",
            padding=10,
        )
        chart_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.chart_canvas = tk.Canvas(chart_frame, height=260, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)

    def refresh(self) -> None:
        report = ReportGenerator().generate_report(self.app.tracker.transactions)
        budget_status = self.app.tracker.get_budget_status()
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
        self.card_values["transaction_count"].set(str(len(self.app.tracker.transactions)))
        self.card_values["budget_count"].set(str(len(self.app.tracker.budgets)))
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
