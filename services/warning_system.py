from collections import defaultdict

from utils.validators import normalize_category


class WarningSystem:
    def __init__(self, low_balance_threshold=100):
        self.low_balance_threshold = low_balance_threshold

    def analyze(self, transactions, budget_limits, current_balance):
        warnings = []

        warnings.extend(self._check_budget_limits(transactions, budget_limits))
        warnings.extend(self._check_low_balance(current_balance))
        warnings.extend(self._check_unusual_spending(transactions))

        return warnings

    def _check_budget_limits(self, transactions, budget_limits):
        category_spending = defaultdict(float)
        warnings = []

        for txn in transactions:
            if txn.get_transaction_type() == "expense":
                category = normalize_category(txn.category)
                category_spending[category] += txn.amount

        for category, budget_limit in budget_limits.items():
            normalized_category = normalize_category(category)
            limit = getattr(budget_limit, "limit", budget_limit)
            spent = category_spending.get(normalized_category, 0)

            if spent > limit:
                exceeded_amount = spent - limit
                warnings.append({
                    "type": "BUDGET_EXCEEDED",
                    "category": normalized_category,
                    "spent": spent,
                    "limit": limit,
                    "exceeded_amount": exceeded_amount,
                    "message": (
                        f"Budget exceeded for {normalized_category}: "
                        f"spent {spent:.2f} / limit {limit:.2f}, "
                        f"exceeded by {exceeded_amount:.2f}"
                    )
                })

        return warnings

    def _check_low_balance(self, current_balance):
        if current_balance < self.low_balance_threshold:
            return [{
                "type": "LOW_BALANCE",
                "balance": current_balance,
                "message": f"Balance is low: {current_balance:.2f}"
            }]

        return []

    def _check_unusual_spending(self, transactions):
        warnings = []
        category_spending = defaultdict(list)

        for txn in transactions:
            if txn.get_transaction_type() == "expense":
                category = normalize_category(txn.category)
                category_spending[category].append(txn)

        for category, expenses in category_spending.items():
            if len(expenses) < 3:
                continue

            sorted_expenses = sorted(expenses, key=lambda transaction: transaction.date)
            latest_expense = sorted_expenses[-1]
            previous_expenses = sorted_expenses[:-1]
            previous_average = (
                sum(transaction.amount for transaction in previous_expenses)
                / len(previous_expenses)
            )

            if latest_expense.amount > 2 * previous_average:
                warnings.append({
                    "type": "UNUSUAL_SPENDING",
                    "category": category,
                    "amount": latest_expense.amount,
                    "average": previous_average,
                    "message": f"Unusual spending detected in {category}"
                })

        return warnings
