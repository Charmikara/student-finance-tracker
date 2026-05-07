# Student Finance Tracker

Student Finance Tracker is a simple Python OOP application for managing student finances. It includes both an interactive command-line interface and a basic Tkinter GUI, while keeping data storage in JSON files.

The project is intentionally small and readable for university coursework.

## Features

- Add income records
- Add expense records
- Set category budgets
- View transactions
- Generate report summaries
- View budget status by category
- Receive warnings for exceeded budgets, low balance, and unusual spending
- Save and load data with JSON
- Load optional sample data from separate JSON files
- Create backups before destructive GUI actions

## Project Structure

```text
student-finance-tracker/
+-- main.py                  # CLI entry point
+-- gui.py                   # Tkinter GUI entry point
+-- models/                  # Transaction, Income, Expense, Budget
+-- services/                # FinanceTracker, reports, warnings
+-- utils/                   # JSON file manager, path helpers, validators
+-- data/                    # Real data, sample data, backups
+-- tests/                   # pytest tests
+-- requirements.txt
+-- README.md
```

## Data Files

The real user data files start empty:

- `data/transactions.json`
- `data/budgets.json`

Sample/demo data is stored separately:

- `data/sample_transactions.json`
- `data/sample_budgets.json`

In the GUI, **Load Sample Data** replaces the current real data with sample data after creating a backup. **Reset All Data** clears the current real data after creating a backup.

Backups are saved in:

```text
data/backups/
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Charmikara/student-finance-tracker.git
cd student-finance-tracker
```

Create and activate a virtual environment:

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

## Run The CLI

```bash
python main.py
```

CLI menu:

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

## Run The GUI

```bash
python gui.py
```

The GUI includes:

- Dashboard overview
- Spending-by-category chart
- Transaction table and form
- Budget table and form
- Warnings list
- Load Sample Data and Reset All Data actions

## Testing

Run the test suite with:

```bash
python -m pytest
```

The tests use temporary files and do not overwrite the real JSON data files.

## Notes

- The project uses JSON storage only.
- No database, API, or web framework is required.
- Runtime backups are ignored by Git, but sample data files are kept in the repository.
