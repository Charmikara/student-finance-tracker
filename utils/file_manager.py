import json


class FileManager:
    def save_transactions(self, transactions, filename):
        data = []

        for txn in transactions:
            data.append({
                "amount": txn.amount,
                "category": txn.category,
                "type": txn.type
            })

        with open(filename, "w") as file:
            json.dump(data, file)

    def load_transactions(self, filename):
        with open(filename, "r") as file:
            data = json.load(file)

        return data