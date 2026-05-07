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
            "id": transactions[0].transaction_id,
            "type": "income",
            "amount": 500.0,
            "category": "salary",
            "description": "part-time job",
            "date": "2026-05-07",
        },
        {
            "id": transactions[1].transaction_id,
            "type": "expense",
            "amount": 25.0,
            "category": "food",
            "description": "lunch",
            "date": "2026-05-07",
        },
    ]

    reloaded_transactions = FileManager().load_transactions(transactions_file)
    assert len(reloaded_transactions) == 2
    assert reloaded_transactions[0].amount == 500
    assert reloaded_transactions[1].category == "food"
    assert reloaded_transactions[0].transaction_id == transactions[0].transaction_id
    assert reloaded_transactions[1].transaction_id == transactions[1].transaction_id


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

    reloaded_budgets = FileManager().load_budgets(budgets_file)
    assert reloaded_budgets["food"].limit == 200
    assert reloaded_budgets["transport"].limit == 80


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


def test_file_manager_loads_utf8_bom_json(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 100,
            "category": "allowance",
            "description": "weekly allowance",
            "date": "2026-05-07",
        },
    ]), encoding="utf-8-sig")

    transactions = FileManager().load_transactions(transactions_file)

    assert len(transactions) == 1
    assert transactions[0].get_transaction_type() == "income"
    assert transactions[0].category == "allowance"


def test_file_manager_loads_old_transactions_without_ids(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "type": "expense",
            "amount": 25,
            "category": "food",
            "description": "lunch",
            "date": "2026-05-07",
        },
    ]))

    transactions = FileManager().load_transactions(transactions_file)

    assert len(transactions) == 1
    assert transactions[0].transaction_id
    assert transactions[0].category == "food"


def test_file_manager_loads_transactions_with_ids(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_text(json.dumps([
        {
            "id": "txn-123",
            "type": "income",
            "amount": 100,
            "category": "salary",
            "description": "job",
            "date": "2026-05-07",
        },
    ]))

    transactions = FileManager().load_transactions(transactions_file)

    assert len(transactions) == 1
    assert transactions[0].transaction_id == "txn-123"


def test_new_transactions_get_ids_and_serialize_them():
    transaction = Income(100, "salary", "job", "2026-05-07")

    assert transaction.transaction_id
    assert transaction.id == transaction.transaction_id
    assert transaction.to_dict()["id"] == transaction.transaction_id


def test_transactions_can_be_created_with_existing_ids():
    transaction = Expense(20, "food", "lunch", "2026-05-07", "existing-id")

    assert transaction.transaction_id == "existing-id"
    assert transaction.to_dict()["id"] == "existing-id"


def test_file_manager_rejects_non_utf8_json_bytes(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    transactions_file.write_bytes(b"\xff\xfe\x00\x00")

    with pytest.raises(ValueError, match="UTF-8 encoded JSON"):
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


def test_finance_tracker_adds_data_and_calculates_balance(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )

    tracker.add_income(1000, "salary", "part-time work", "2026-05-07")
    tracker.add_expense(125, "Food", "groceries", "2026-05-07")
    tracker.add_budget(" food ", 200)

    assert tracker.get_total_income() == 1000
    assert tracker.get_total_expenses() == 125
    assert tracker.get_balance() == 875
    assert tracker.budgets["food"].limit == 200


def test_finance_tracker_clears_data(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_income(100, "allowance", "weekly allowance", "2026-05-07")
    tracker.add_budget("food", 50)

    tracker.clear_data()

    assert tracker.transactions == []
    assert tracker.budgets == {}


def test_finance_tracker_loads_sample_data(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"
    sample_transactions_file = tmp_path / "sample_transactions.json"
    sample_budgets_file = tmp_path / "sample_budgets.json"

    transactions_file.write_text("[]")
    budgets_file.write_text("[]")
    sample_transactions_file.write_text(json.dumps([
        {
            "type": "income",
            "amount": 300,
            "category": "allowance",
            "description": "monthly allowance",
            "date": "2026-05-07",
        },
    ]))
    sample_budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 100},
    ]))

    tracker = FinanceTracker(
        transactions_file,
        budgets_file,
        sample_transactions_file,
        sample_budgets_file,
    )

    tracker.load_sample_data()

    assert len(tracker.transactions) == 1
    assert tracker.transactions[0].category == "allowance"
    assert tracker.budgets["food"].limit == 100


def test_finance_tracker_backs_up_current_data(tmp_path):
    transactions_file = tmp_path / "transactions.json"
    budgets_file = tmp_path / "budgets.json"
    backup_dir = tmp_path / "backups"
    transactions_file.write_text(json.dumps([
        {
            "type": "expense",
            "amount": 20,
            "category": "food",
            "description": "lunch",
            "date": "2026-05-07",
        },
    ]))
    budgets_file.write_text(json.dumps([
        {"category": "food", "limit": 100},
    ]))

    tracker = FinanceTracker(
        transactions_file,
        budgets_file,
        tmp_path / "sample_transactions.json",
        tmp_path / "sample_budgets.json",
        backup_dir,
    )

    backups = tracker.backup_current_data()

    assert len(backups) == 2
    assert all(path.exists() for path in backups)
    assert {path.name.split("_")[0] for path in backups} == {"transactions", "budgets"}


def test_finance_tracker_delete_invalid_transaction_index_raises(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )

    with pytest.raises(IndexError, match="out of range"):
        tracker.delete_transaction_by_index(0)


def test_finance_tracker_deletes_transaction_by_id(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_income(100, "allowance", "weekly allowance", "2026-05-07")
    transaction_id = tracker.transactions[0].transaction_id

    tracker.delete_transaction_by_id(transaction_id)

    assert tracker.transactions == []


def test_finance_tracker_update_transaction_keeps_same_id(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_expense(20, "food", "lunch", "2026-05-07")
    transaction_id = tracker.transactions[0].transaction_id

    tracker.update_transaction(
        transaction_id,
        "expense",
        35,
        "transport",
        "bus pass",
        "2026-05-08",
    )

    transaction = tracker.get_transaction_by_id(transaction_id)
    assert transaction.transaction_id == transaction_id
    assert transaction.amount == 35
    assert transaction.category == "transport"
    assert transaction.description == "bus pass"
    assert transaction.date == "2026-05-08"


def test_finance_tracker_update_transaction_changes_income_to_expense(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_income(100, "allowance", "weekly allowance", "2026-05-07")
    transaction_id = tracker.transactions[0].transaction_id

    tracker.update_transaction(
        transaction_id,
        "expense",
        40,
        "food",
        "groceries",
        "2026-05-08",
    )

    transaction = tracker.get_transaction_by_id(transaction_id)
    assert transaction.get_transaction_type() == "expense"
    assert tracker.get_balance() == -40


def test_finance_tracker_update_transaction_changes_expense_to_income(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_expense(50, "food", "groceries", "2026-05-07")
    transaction_id = tracker.transactions[0].transaction_id

    tracker.update_transaction(
        transaction_id,
        "income",
        200,
        "salary",
        "part-time job",
        "2026-05-08",
    )

    transaction = tracker.get_transaction_by_id(transaction_id)
    assert transaction.get_transaction_type() == "income"
    assert tracker.get_balance() == 200


def test_finance_tracker_invalid_transaction_id_raises(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )

    with pytest.raises(ValueError, match="Transaction not found"):
        tracker.get_transaction_by_id("missing-id")

    with pytest.raises(ValueError, match="Transaction not found"):
        tracker.delete_transaction_by_id("missing-id")

    with pytest.raises(ValueError, match="Transaction not found"):
        tracker.update_transaction(
            "missing-id",
            "expense",
            10,
            "food",
            "snack",
            "2026-05-07",
        )


def test_finance_tracker_invalid_update_type_raises(tmp_path):
    tracker = FinanceTracker(
        tmp_path / "transactions.json",
        tmp_path / "budgets.json",
    )
    tracker.add_income(100, "allowance", "weekly allowance", "2026-05-07")

    with pytest.raises(ValueError, match="Transaction type"):
        tracker.update_transaction(
            tracker.transactions[0].transaction_id,
            "transfer",
            10,
            "savings",
            "move money",
            "2026-05-07",
        )


def test_model_validation_rejects_invalid_values():
    with pytest.raises(ValueError, match="greater than 0"):
        Income(0, "salary", "job", "2026-05-07")

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        Expense(10, "food", "lunch", "05-07-2026")

    with pytest.raises(ValueError, match="Category cannot be empty"):
        Expense(10, " ", "lunch", "2026-05-07")

    with pytest.raises(ValueError, match="Budget limit must be greater than 0"):
        Budget("food", 0)


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


def test_report_generator_empty_report():
    report = ReportGenerator().generate_report([])

    assert report == {
        "total_income": 0,
        "total_expense": 0,
        "balance": 0,
        "category_spending": {},
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


def test_warning_system_formats_low_balance_with_two_decimals():
    warnings = WarningSystem(low_balance_threshold=100).analyze(
        [],
        {},
        current_balance=50,
    )

    assert warnings == [{
        "type": "LOW_BALANCE",
        "balance": 50,
        "message": "Balance is low: 50.00",
    }]


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
