from utils.validators import normalize_category


class ReportGenerator:
    def generate_report(self, transactions):
        total_income, total_expense = self._calculate_totals(transactions)
        category_spending = self._calculate_category_spending(transactions)

        report = {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "category_spending": category_spending
        }

        return report

    def _calculate_totals(self, transactions):
        total_income = 0
        total_expense = 0

        for txn in transactions:
            if txn.get_transaction_type() == "income":
                total_income += txn.amount
            elif txn.get_transaction_type() == "expense":
                total_expense += txn.amount

        return total_income, total_expense

    def _calculate_category_spending(self, transactions):
        category_spending = {}

        for txn in transactions:
            if txn.get_transaction_type() == "expense":
                category = normalize_category(txn.category)
                if category not in category_spending:
                    category_spending[category] = 0

                category_spending[category] += txn.amount

        return category_spending
