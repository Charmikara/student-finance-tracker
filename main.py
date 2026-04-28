from services.warning_system import WarningSystem
from services.report_generator import ReportGenerator
from utils.file_manager import FileManager


class Transaction:
    def __init__(self, amount, category, type):
        self.amount = amount
        self.category = category
        self.type = type


# Initial transactions
transactions = [
    Transaction(50, "food", "expense"),
    Transaction(80, "food", "expense"),
    Transaction(300, "food", "expense"),
    Transaction(30, "transport", "expense"),
    Transaction(20, "transport", "expense"),
    Transaction(1000, "salary", "income")
]

budget_limits = {
    "food": 100,
    "transport": 60
}

current_balance = 50


# Create objects
warning_system = WarningSystem()
report_generator = ReportGenerator()
file_manager = FileManager()


# Save transactions to file
file_manager.save_transactions(transactions, "data/transactions.json")

# Load transactions from file
loaded_data = file_manager.load_transactions("data/transactions.json")

# Convert loaded data back to Transaction objects
transactions = []
for item in loaded_data:
    transactions.append(Transaction(item["amount"], item["category"], item["type"]))


# Run systems
warnings = warning_system.analyze(transactions, budget_limits, current_balance)
report = report_generator.generate_report(transactions)


# Output
print("---- REPORT ----")
print(f"Total Income: {report['total_income']}")
print(f"Total Expense: {report['total_expense']}")
print(f"Balance: {report['balance']}")

print("\nCategory Spending:")
for category, amount in report["category_spending"].items():
    print(f"- {category}: {amount}")

print("\n---- WARNINGS ----")
for w in warnings:
    print(f"{w['type']}: {w['message']}")