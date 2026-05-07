from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"
SAMPLE_TRANSACTIONS_FILE = DATA_DIR / "sample_transactions.json"
SAMPLE_BUDGETS_FILE = DATA_DIR / "sample_budgets.json"
BACKUP_DIR = DATA_DIR / "backups"
