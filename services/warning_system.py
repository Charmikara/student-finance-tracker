from collections import defaultdict


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
                category_spending[txn.category] += txn.amount

        for category, budget_limit in budget_limits.items():
            limit = getattr(budget_limit, "limit", budget_limit)
            spent = category_spending.get(category, 0)

            if spent > limit:
                warnings.append({
                    "type": "BUDGET_EXCEEDED",
                    "category": category,
                    "spent": spent,
                    "limit": limit,
                    "message": f"{category} budget exceeded by {spent - limit}"
                })

        return warnings

    def _check_low_balance(self, current_balance):
        if current_balance < self.low_balance_threshold:
            return [{
                "type": "LOW_BALANCE",
                "balance": current_balance,
                "message": f"Balance is low: {current_balance}"
            }]

        return []

    def _check_unusual_spending(self, transactions):
        warnings = []
        category_spending = defaultdict(list)

        for txn in transactions:
            if txn.get_transaction_type() == "expense":
                category_spending[txn.category].append(txn.amount)

        for category, amounts in category_spending.items():
            if len(amounts) < 3:
                continue

            avg = sum(amounts) / len(amounts)
            last = amounts[-1]

            if last > 2 * avg:
                warnings.append({
                    "type": "UNUSUAL_SPENDING",
                    "category": category,
                    "amount": last,
                    "average": avg,
                    "message": f"Unusual spending detected in {category}"
                })

        return warnings
