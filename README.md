# Student Finance Tracker

Student Finance Tracker is a Python object-oriented command-line application for managing simple student finances. It lets users record income and expenses, set category budgets, view reports, receive spending warnings, and save/load data using JSON files.

This project is designed to be simple, readable, and suitable for university coursework.

## Features

- Add income records
- Add expense records
- Set category budgets
- View all transactions
- Generate finance reports
- View budget status by category
- Receive warnings for exceeded budgets, low balance, and unusual spending
- Save and load transactions and budgets with JSON

## Project Structure

```text
student-finance-tracker/
+-- main.py
+-- gui.py
+-- models/
+-- services/
+-- utils/
+-- data/
+-- tests/
+-- requirements.txt
+-- README.md
```

### `main.py`

Contains the interactive command-line menu. It creates a `FinanceTracker` object, loads existing JSON data, and lets the user choose actions such as adding transactions, viewing reports, checking budgets, and saving data.

### `gui.py`

Contains a simple Tkinter interface for the same tracker. It lets the user add income, expenses, and budgets, then refreshes transactions, reports, budget status, and warnings.

### `models/`

Contains the main OOP data classes:

- `Transaction`: base class for financial transactions
- `Income`: represents income records
- `Expense`: represents expense records
- `Budget`: represents a budget for a spending category

### `services/`

Contains the main application logic:

- `FinanceTracker`: manages transactions, budgets, totals, and JSON loading/saving
- `ReportGenerator`: creates report summaries from transactions
- `WarningSystem`: creates warnings for exceeded budgets, low balance, and unusual spending

### `utils/`

Contains helper code such as `FileManager`, which handles reading from and writing to JSON files.

### `data/`

Stores sample and saved application data:

- `transactions.json`
- `budgets.json`

The application loads sample data from these files when it starts and saves changes back to them.

### `tests/`

Contains pytest tests for JSON persistence, finance tracker loading, report generation, and warning logic.

## Setup

Clone the repository:

```bash
git clone https://github.com/Charmikara/student-finance-tracker.git
cd student-finance-tracker
```

Create and activate a virtual environment if needed:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install requirements:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

Run the optional Tkinter GUI:

```bash
python gui.py
```

## Sample Usage

When the application runs, it shows this menu:

```text
Student Finance Tracker
1. Add income
2. Add expense
3. Add budget
4. View transactions
5. View report
6. View budget status
7. View warnings
8. Save and exit
```

Example workflow:

1. Choose `1` to add income.
2. Choose `2` to add an expense.
3. Choose `3` to add or update a budget.
4. Choose `5` to view a report summary.
5. Choose `7` to view warnings.
6. Choose `8` to save and exit.

## Testing

Run the test suite with:

```bash
python -m pytest
```

The tests use temporary files where needed, so they do not depend on or overwrite the real sample JSON files.

## Notes

- Sample transactions are stored in `data/transactions.json`.
- Sample budgets are stored in `data/budgets.json`.
- The project uses JSON storage only.
- The code is intentionally kept simple to demonstrate core OOP concepts.
