import json

import pytest

from models.budget import Budget
from models.expense import Expense
from models.income import Income
from services.finance_tracker import FinanceTracker
from services.report_generator import ReportGenerator
from services.warning_system import WarningSystem
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


def test_file_manager_handles_empty_files(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"
    transactions_file.write_text("")
    budgets_file.write_text("")

    file_manager = FileManager()

    assert file_manager.load_transactions(transactions_file) == []
    assert file_manager.load_budgets(budgets_file) == {}


def test_file_manager_handles_missing_files(tmp_path):
    file_manager = FileManager()

    assert file_manager.load_transactions(tmp_path / "missing_transactions.json") == []
    assert file_manager.load_budgets(tmp_path / "missing_budgets.json") == {}


def test_file_manager_rejects_malformed_json(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text("{bad json")

    with pytest.raises(ValueError, match="not valid JSON"):
        FileManager().load_transactions(transactions_file)


def test_file_manager_rejects_missing_transaction_fields(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "expense",
            "amount": 20,
            "category": "food",
            "date": "2026-05-07",
        },
    ]))

    with pytest.raises(ValueError, match="missing required field"):
        FileManager().load_transactions(transactions_file)


def test_file_manager_rejects_missing_budget_fields(tmp_path):
    budgets_file = tmp_path / "budgets.json"
    budgets_file.write_text(json.dumps([
        {"category": "food"},
    ]))

    with pytest.raises(ValueError, match="missing required field"):
        FileManager().load_budgets(budgets_file)


def test_file_manager_rejects_unknown_transaction_type(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "transfer",
            "amount": 50,
            "category": "savings",
            "description": "move money",
            "date": "2026-05-07",
        },
    ]))

    with pytest.raises(ValueError, match="Unknown transaction type"):
        FileManager().load_transactions(transactions_file)


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


def test_finance_tracker_loads_sample_data_and_saves_to_active_files(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"
    sample_transactions_file = tmp_path / "sample_transactions.json"
    sample_budgets_file = tmp_path / "sample_budgets.json"

    transactions_file.write_text("[]")
    budgets_file.write_text("[]")
    sample_transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 500,
            "category": "salary",
            "description": "part-time job",
            "date": "2026-05-07",
        },
        {
            "type": "expense",
            "amount": 50,
            "category": "food",
            "description": "groceries",
            "date": "2026-05-07",
        },
    ]))
    sample_budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 200},
    ]))

    tracker = FinanceTracker(
        transactions_file,
        budgets_file,
        sample_transactions_file,
        sample_budgets_file,
    )

    tracker.load_sample_data()
    tracker.save()
    reloaded = FinanceTracker(transactions_file, budgets_file)

    assert len(reloaded.transactions) == 2
    assert reloaded.get_balance() == 450
    assert reloaded.budgets["food"].limit == 200


def test_finance_tracker_clears_data_and_saves_empty_files(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 500,
            "category": "salary",
            "description": "part-time job",
            "date": "2026-05-07",
        },
    ]))
    budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 200},
    ]))

    tracker = FinanceTracker(transactions_file, budgets_file)
    tracker.clear_data()
    tracker.save()

    assert json.loads(transactions_file.read_text()) == []
    assert json.loads(budgets_file.read_text()) == []


def test_finance_tracker_deletes_transaction_and_budget(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_income(500, "salary", "part-time job", "2026-05-07")
    tracker.add_expense(50, "food", "groceries", "2026-05-07")
    tracker.add_budget("food", 200)

    tracker.delete_transaction_by_index(0)
    tracker.delete_budget(" Food ")

    assert len(tracker.transactions) == 1
    assert tracker.transactions[0].get_transaction_type() == "expense"
    assert tracker.budgets == {}


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


def test_category_normalization_for_reports_and_budget_status(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )

    tracker.add_expense(40, " Food ", "groceries", "2026-05-07")
    tracker.add_expense(60, "FOOD", "lunch", "2026-05-08")
    tracker.add_budget(" food ", 90)

    report = ReportGenerator().generate_report(tracker.transactions)
    budget_status = tracker.get_budget_status()

    assert report["category_spending"] == {"food": 100}
    assert budget_status["food"]["spent"] == 100
    assert budget_status["food"]["limit"] == 90
    assert budget_status["food"]["exceeded"] is True


def test_warning_system_detects_food_budget_exceeded():
    transactions = [
        Expense(250, "food", "weekly groceries", "2026-05-07"),
    ]
    budgets = {
        "food": Budget("food", 200),
    }

    warnings = WarningSystem().analyze(transactions, budgets, current_balance=500)

    assert len(warnings) == 1
    assert warnings[0]["type"] == "BUDGET_EXCEEDED"
    assert warnings[0]["message"] == (
        "Budget exceeded for food: spent 250.00 / limit 200.00, "
        "exceeded by 50.00"
    )


def test_warning_system_matches_subscriptions_case_and_whitespace():
    transactions = [
        Expense(60, " Subscriptions ", "music plan", "2026-05-07"),
        Expense(63, "subscriptions", "cloud storage", "2026-05-07"),
    ]
    budgets = {
        "Subscriptions": Budget("Subscriptions", 100),
    }

    warnings = WarningSystem().analyze(transactions, budgets, current_balance=500)

    assert len(warnings) == 1
    assert warnings[0]["category"] == "subscriptions"
    assert warnings[0]["spent"] == 123
    assert warnings[0]["limit"] == 100
    assert warnings[0]["exceeded_amount"] == 23
    assert warnings[0]["message"] == (
        "Budget exceeded for subscriptions: spent 123.00 / limit 100.00, "
        "exceeded by 23.00"
    )


def test_warning_system_returns_multiple_budget_warnings_together():
    transactions = [
        Expense(250, "food", "weekly groceries", "2026-05-07"),
        Expense(123, "subscriptions", "monthly plans", "2026-05-07"),
    ]
    budgets = {
        "food": Budget("food", 200),
        "subscriptions": Budget("subscriptions", 100),
    }

    warnings = WarningSystem().analyze(transactions, budgets, current_balance=500)
    budget_warnings = [
        warning for warning in warnings
        if warning["type"] == "BUDGET_EXCEEDED"
    ]

    assert len(budget_warnings) == 2
    assert {warning["category"] for warning in budget_warnings} == {
        "food",
        "subscriptions",
    }


def test_warning_system_keeps_unusual_spending_with_budget_warning():
    transactions = [
        Expense(10, "food", "snack", "2026-05-01"),
        Expense(10, "food", "lunch", "2026-05-02"),
        Expense(100, "food", "large shop", "2026-05-03"),
    ]
    budgets = {
        "food": Budget("food", 50),
    }

    warnings = WarningSystem().analyze(transactions, budgets, current_balance=500)

    warning_types = [warning["type"] for warning in warnings]
    assert "BUDGET_EXCEEDED" in warning_types
    assert "UNUSUAL_SPENDING" in warning_types


def test_warning_system_uses_latest_expense_by_date_for_unusual_spending():
    transactions = [
        Expense(300, "food", "old large shop", "2026-05-01"),
        Expense(50, "food", "groceries", "2026-05-02"),
        Expense(60, "food", "new groceries", "2026-05-03"),
    ]

    warnings = WarningSystem().analyze(transactions, {}, current_balance=500)

    assert [
        warning for warning in warnings
        if warning["type"] == "UNUSUAL_SPENDING"
    ] == []


def test_warning_system_compares_latest_against_previous_average():
    transactions = [
        Expense(50, "food", "groceries", "2026-05-01"),
        Expense(60, "food", "lunch", "2026-05-02"),
        Expense(200, "food", "large shop", "2026-05-03"),
    ]

    warnings = WarningSystem().analyze(transactions, {}, current_balance=500)
    unusual_warnings = [
        warning for warning in warnings
        if warning["type"] == "UNUSUAL_SPENDING"
    ]

    assert len(unusual_warnings) == 1
    assert unusual_warnings[0]["amount"] == 200
    assert unusual_warnings[0]["average"] == 55
