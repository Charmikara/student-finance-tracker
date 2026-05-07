import json

from models.budget import Budget
from models.expense import Expense
from models.income import Income
from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from utils.file_manager import FileManager


def test_file_manager_loads_transactions(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 500,
            "category": "salary",
            "description": "part-time job",
            "date": "2026-05-07",
        },
        {
            "type": "expense",
            "amount": 25,
            "category": "food",
            "description": "lunch",
            "date": "2026-05-07",
        },
    ]))

    transactions = FileManager().load_transactions(transactions_file)

    assert len(transactions) == 2
    assert transactions[0].get_transaction_type() == "income"
    assert transactions[0].amount == 500
    assert transactions[1].get_transaction_type() == "expense"
    assert transactions[1].category == "food"


def test_file_manager_saves_transactions(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions = [
        Income(500, "salary", "part-time job", "2026-05-07"),
        Expense(25, "food", "lunch", "2026-05-07"),
    ]

    FileManager().save_transactions(transactions, transactions_file)

    saved_data = json.loads(transactions_file.read_text())
    assert saved_data == [
        {
            "type": "income",
            "amount": 500.0,
            "category": "salary",
            "description": "part-time job",
            "date": "2026-05-07",
        },
        {
            "type": "expense",
            "amount": 25.0,
            "category": "food",
            "description": "lunch",
            "date": "2026-05-07",
        },
    ]


def test_file_manager_loads_budgets(tmp_path):
    budgets_file = tmp_path / "budgets.json"
    budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 200},
        {"category": "transport", "limit": 80},
    ]))

    budgets = FileManager().load_budgets(budgets_file)

    assert len(budgets) == 2
    assert budgets["food"].limit == 200
    assert budgets["transport"].category == "transport"


def test_file_manager_saves_budgets(tmp_path):
    budgets_file = tmp_path / "budgets.json"
    budgets = {
        "food": Budget("food", 200),
        "transport": Budget("transport", 80),
    }

    FileManager().save_budgets(budgets, budgets_file)

    saved_data = json.loads(budgets_file.read_text())
    assert saved_data == [
        {"category": "food", "limit": 200.0},
        {"category": "transport", "limit": 80.0},
    ]


def test_finance_tracker_loads_from_json_files(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"

    transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 1000,
            "category": "salary",
            "description": "monthly salary",
            "date": "2026-05-07",
        },
        {
            "type": "expense",
            "amount": 100,
            "category": "food",
            "description": "groceries",
            "date": "2026-05-07",
        },
    ]))
    budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 200},
    ]))

    tracker = FinanceTracker(transactions_file, budgets_file)

    assert len(tracker.transactions) == 2
    assert tracker.get_balance() == 900
    assert tracker.budgets["food"].limit == 200


def test_report_generator_calculates_summary_and_categories():
    transactions = [
        Income(1000, "salary", "monthly salary", "2026-05-07"),
        Expense(100, "food", "groceries", "2026-05-07"),
        Expense(50, "food", "lunch", "2026-05-07"),
        Expense(25, "transport", "bus pass", "2026-05-07"),
    ]

    report = ReportGenerator().generate_report(transactions)

    assert report["total_income"] == 1000
    assert report["total_expense"] == 175
    assert report["balance"] == 825
    assert report["category_spending"] == {
        "food": 150,
        "transport": 25,
    }
