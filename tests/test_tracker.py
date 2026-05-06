import unittest
from pathlib import Path

from services.finance_tracker import FinanceTracker


class FinanceTrackerTest(unittest.TestCase):
    def setUp(self):
        self.transactions_file = Path("data/test_transactions_unit.json")
        self.budgets_file = Path("data/test_budgets_unit.json")

    def tearDown(self):
        self.transactions_file.unlink(missing_ok=True)
        self.budgets_file.unlink(missing_ok=True)

    def test_tracks_income_expenses_and_balance(self):
        tracker = FinanceTracker(self.transactions_file, self.budgets_file)

        tracker.add_income(1000, "salary", "monthly pay", "2026-05-07")
        tracker.add_expense(125, "food", "groceries", "2026-05-07")

        self.assertEqual(tracker.get_total_income(), 1000)
        self.assertEqual(tracker.get_total_expenses(), 125)
        self.assertEqual(tracker.get_balance(), 875)

    def test_saves_and_loads_json_storage(self):
        tracker = FinanceTracker(self.transactions_file, self.budgets_file)
        tracker.add_expense(50, "transport", "bus pass", "2026-05-07")
        tracker.add_budget("transport", 75)
        tracker.save()

        reloaded = FinanceTracker(self.transactions_file, self.budgets_file)

        self.assertEqual(len(reloaded.transactions), 1)
        self.assertEqual(reloaded.transactions[0].category, "transport")
        self.assertIn("transport", reloaded.budgets)


if __name__ == "__main__":
    unittest.main()
