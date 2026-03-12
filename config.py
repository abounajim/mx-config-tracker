# ============================================================
# MX Config Tracker — config.py
# ============================================================

# ── Mode ────────────────────────────────────────────────────
# "csv" → reads CSVs from input/  (drop files manually)
# "db"  → runs .sql files from queries/ against the database
MODE = "csv"

# ── Folders ─────────────────────────────────────────────────
INPUT_FOLDER = "input"

# ── GitHub ──────────────────────────────────────────────────
GITHUB_REMOTE = "https://abounajim@github.com/abounajim/mx-config-tracker.git"

# ── Git identity ─────────────────────────────────────────────
GIT_USER_NAME  = "Config Tracker"
GIT_USER_EMAIL = "config-tracker@sequel.com"

# ── Environment ──────────────────────────────────────────────
# Subfolder under snapshots/: prod / tst01 / tst02
ENVIRONMENT = "prod"

# ── DB (only used when MODE = "db") ─────────────────────────
DB_TYPE = "mssql"

DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=your_server;"
    "DATABASE=your_database;"
    "UID=your_username;"
    "PWD=your_password;"
)
