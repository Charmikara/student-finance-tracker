# Student Finance Tracker - Project Report

**Authors:** Charmikara, Pratham  
**Course:** Object-Oriented Programming  
**Repository:** https://github.com/Charmikara/student-finance-tracker  
**Date:** May 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Problem Definition and Requirements](#2-problem-definition-and-requirements)
- [3. Design and Implementation](#3-design-and-implementation)
- [4. Development Process](#4-development-process)
- [5. Results and Demonstration](#5-results-and-demonstration)
- [6. Testing and Validation](#6-testing-and-validation)
- [7. Conclusion and Future Work](#7-conclusion-and-future-work)
- [8. Setup and Installation](#8-setup-and-installation)

---

## 1. Introduction

### 1.1 Purpose and Objectives of the Application

Student Finance Tracker helps students manage personal finances in a simple offline application. Users can track income, expenses, category budgets, reports, and warning messages. Data is stored locally in JSON files, so the project does not require online accounts, databases, or web services.

The project also demonstrates object-oriented programming principles through models, services, validation, persistence, a command-line interface, and a Tkinter graphical interface.

Objectives:

- Add, edit, and delete transactions.
- Categorize spending.
- Set category budgets.
- Generate report summaries.
- Warn about exceeded budgets, low balance, and unusual spending.
- Save and load data safely using JSON.
- Use OOP concepts clearly.

### 1.2 Brief Overview of Chosen Project

The chosen project is **Student Finance Tracker**, a Python OOP application for student budgeting. The CLI starts from `main.py`, and the Tkinter GUI starts from `gui.py`. GUI components are organized in `ui/`, domain models are in `models/`, business logic is in `services/`, file handling and validation helpers are in `utils/`, JSON files are in `data/`, and automated tests are in `tests/`.

---

## 2. Problem Definition and Requirements

### 2.1 Description of the Problem

Students often have irregular income from allowances, part-time work, or freelance tasks, while also managing recurring expenses such as food, transport, rent, study materials, and entertainment. It is easy to lose track of spending by category, especially when using informal notes or memory.

Many budgeting tools are complex or require online accounts. This application provides a simple local solution focused on student budgeting and coursework-level OOP design.

### 2.2 Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-1 | Add income records. |
| FR-2 | Add expense records. |
| FR-3 | Edit selected transactions in the GUI. |
| FR-4 | Delete selected transactions in the GUI. |
| FR-5 | Set and delete category budgets. |
| FR-6 | View transactions. |
| FR-7 | Generate report summaries. |
| FR-8 | View budget status. |
| FR-9 | Show exceeded budget warnings. |
| FR-10 | Show low balance warnings. |
| FR-11 | Show unusual spending warnings. |
| FR-12 | Save and load data using JSON. |
| FR-13 | Load optional sample data. |
| FR-14 | Reset all real data after backup. |
| FR-15 | Use stable transaction IDs for safer editing/deleting. |

### 2.3 Non-Functional Requirements

| Requirement | Description |
| --- | --- |
| Usability | The CLI menu and GUI tabs should be easy to understand. |
| Reliability | JSON loading, saving, and validation should handle common errors clearly. |
| Maintainability | Code should be split into models, services, utilities, and UI modules. |
| Portability | The app should run with Python standard library features plus pytest for testing. |
| Data integrity | Atomic JSON saving and backups should reduce accidental data loss. |
| Testability | Core model, service, warning, report, and file logic should be testable with pytest. |
| Simplicity/readability | The design should remain suitable for university OOP coursework. |

---

## 3. Design and Implementation

### 3.1 Object-Oriented Design Principles Used

#### Encapsulation

Models keep important values in private attributes such as `_amount`, `_category`, and `_date`. `FinanceTracker` stores `_transactions` and `_budgets` internally and exposes controlled methods for adding, updating, deleting, loading, and saving data. Validation is handled inside model constructors and utility functions.

#### Inheritance

`Income` and `Expense` inherit from the abstract `Transaction` base class. This avoids duplicating shared transaction fields such as amount, category, description, date, and transaction ID.

#### Abstraction

`Transaction` is an abstract base class with `get_transaction_type()`. Subclasses define the exact transaction type while sharing common behavior.

#### Polymorphism

`ReportGenerator` and `WarningSystem` process both `Income` and `Expense` objects through the same transaction interface. They call methods such as `get_transaction_type()` without needing separate code paths for every subclass.

#### Composition

`FinanceTracker` combines models and services. It stores transaction and budget objects, uses `FileManager` for JSON persistence, and works with reporting and warning logic through service classes.

### 3.2 Class Diagrams and Structure

Text-based class/architecture diagram:

```text
StudentFinanceCLI
  -> FinanceTracker

StudentFinanceGUI
  -> DashboardTab
  -> TransactionsTab
  -> BudgetsTab
  -> FinanceTracker

FinanceTracker
  -> Transaction
      -> Income
      -> Expense
  -> Budget
  -> FileManager
  -> ReportGenerator
  -> WarningSystem

FileManager
  -> JSON files in data/
```

Current project structure:

```text
student-finance-tracker/
  main.py
  gui.py
  ui/
    app.py
    dashboard_tab.py
    transactions_tab.py
    budgets_tab.py
    constants.py
  models/
    transaction.py
    income.py
    expense.py
    budget.py
  services/
    finance_tracker.py
    report_generator.py
    warning_system.py
  utils/
    file_manager.py
    paths.py
    validators.py
  data/
    transactions.json
    budgets.json
    sample_transactions.json
    sample_budgets.json
    backups/
  tests/
    test_tracker.py
  requirements.txt
  README.md
```

### 3.3 Key Algorithms and Data Structures Implemented

#### Atomic JSON Saving

`FileManager` writes JSON data to a temporary file in the same directory, flushes the content, calls `os.fsync()`, and then replaces the original file using `os.replace()`. This reduces the chance of leaving a half-written JSON file if saving is interrupted.

#### JSON Loading and Validation

JSON loading handles missing files, empty files, malformed JSON, and non-UTF-8 input. Files are read with `utf-8-sig` so UTF-8 files with a byte order mark can still load. Required fields are checked before creating model objects, and unknown transaction types raise clear errors.

#### Category Normalization

Categories are normalized by stripping whitespace and converting text to lowercase. This makes values such as `Food`, ` food `, and `FOOD` behave as the same category.

#### Budget Status Calculation

Expenses are grouped by category and compared with each category budget limit. The budget status includes the limit, amount spent, remaining amount, and whether the budget is exceeded.

#### Warning Generation

The warning system creates:

- Budget exceeded warnings.
- Low balance warnings.
- Unusual spending warnings based on the latest expense compared with the previous average in the same category.

#### Transaction ID Based Editing/Deleting

Each transaction has a stable UUID. The GUI uses this transaction ID rather than the table row position when editing or deleting records. Old JSON records without IDs still load successfully; a new ID is generated in memory and saved later.

#### Data Structures

- A list stores transactions.
- A dictionary stores budgets by category.
- `defaultdict` is used for category totals in warning logic.
- JSON arrays store transactions and budgets on disk.

---

## 4. Development Process

### 4.1 Tools and Environment

Real tools and libraries used:

- Python 3
- Tkinter
- JSON
- pytest
- Git and GitHub
- VS Code
- Standard library modules including `pathlib`, `tempfile`, `os`, `shutil`, `uuid`, and `datetime`

### 4.2 Steps Followed During Development

1. Planned the student finance tracker idea.
2. Defined core requirements.
3. Designed OOP models.
4. Implemented `Transaction`, `Income`, `Expense`, and `Budget`.
5. Built the `FinanceTracker` service.
6. Added `ReportGenerator` and `WarningSystem`.
7. Added `FileManager` with JSON persistence.
8. Built the CLI in `main.py`.
9. Built the GUI in `gui.py`.
10. Separated sample data from real data.
11. Added backups before destructive sample-loading and reset actions.
12. Added transaction IDs and GUI editing.
13. Refactored the GUI into tab modules under `ui/`.
14. Added pytest tests.
15. Fixed issues such as JSON encoding/BOM handling and fragile row-index deletion.

---

## 5. Results and Demonstration

### 5.1 Application Features

The application supports both CLI and GUI workflows. The CLI provides a simple menu for adding income, adding expenses, setting budgets, viewing transactions, reports, budget status, warnings, and saving data. The GUI adds a dashboard, transaction table, editing and deleting selected transactions, budget management, warning display, sample data loading, and reset with backup.

CLI menu example:

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

### 5.2 Screenshots or Relevant Visuals

Screenshot placeholders:

- [Insert screenshot: Dashboard tab]
- [Insert screenshot: Transactions tab showing add/edit/delete]
- [Insert screenshot: Budgets and Warnings tab]
- [Insert screenshot: CLI menu]
- [Insert screenshot: sample data loaded]

Sample transaction JSON structure:

```json
[
  {
    "id": "example-transaction-id",
    "type": "expense",
    "amount": 25.0,
    "category": "food",
    "description": "Lunch",
    "date": "2026-05-07"
  }
]
```

Sample report output:

```text
Total income: 1000.00
Total expenses: 175.00
Balance: 825.00

Expenses by category:
food: 150.00
transport: 25.00
```

Sample warning output:

```text
Budget exceeded for food: spent 250.00 / limit 200.00, exceeded by 50.00
Balance is low: 50.00
Unusual spending detected in food
```

---

## 6. Testing and Validation

### 6.1 Description of Testing Procedures

Tests are written using pytest. Temporary files are used for persistence tests so the real JSON data files are not overwritten. Manual GUI testing is also used because Tkinter interface behavior is difficult to fully test with unit tests.

Tested areas include:

- Model validation.
- `FileManager` save/load behavior.
- Missing files.
- Malformed JSON.
- UTF-8 BOM handling.
- Non-UTF-8 encoding errors.
- `FinanceTracker` add/update/delete behavior.
- Transaction ID compatibility.
- Report generation.
- Warning generation.
- Budget status calculation.

### 6.2 Test Results and Issues Resolved

Validation commands used:

```bash
python -m pytest
python -m py_compile main.py gui.py
```

At the time this report was updated, these commands were run successfully:

- `python -m pytest`: 39 tests passed.
- `python -m py_compile main.py gui.py`: passed.

Issues resolved during development:

- Real data was separated from sample data.
- Backups were added before sample replacement and reset actions.
- JSON encoding/BOM handling was improved.
- Transaction deletion no longer depends on table row index.
- The GUI was refactored from one large file into smaller tab modules.
- Validation prevents invalid dates, empty text fields, and non-positive amounts.

---

## 7. Conclusion and Future Work

### 7.1 Summary of Achievements

Student Finance Tracker is a working Python OOP finance tracker with both CLI and Tkinter GUI interfaces. It demonstrates encapsulation, inheritance, abstraction, polymorphism, and composition. The application persists data with JSON, validates user input, includes sample data, creates backups before destructive data replacement/reset actions, and supports safer transaction editing/deleting through stable transaction IDs.

### 7.2 Recommendations for Future Improvements

Possible future improvements include:

- Transaction filters.
- Monthly reports.
- Better charts.
- CSV/PDF export.
- Recurring transactions.
- Optional SQLite database storage.
- Packaged executable.
- Improved GUI styling.

---

## 8. Setup and Installation

Clone the repository:

```bash
git clone https://github.com/Charmikara/student-finance-tracker.git
cd student-finance-tracker
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Activate the virtual environment on macOS/Linux:

```bash
source venv/bin/activate
```

Install requirements:

```bash
python -m pip install -r requirements.txt
```

Run the CLI:

```bash
python main.py
```

Run the GUI:

```bash
python gui.py
```

Run tests:

```bash
python -m pytest
```
