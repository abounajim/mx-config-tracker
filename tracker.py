"""
MX Config Tracker — tracker.py
────────────────────────────────────────────────────────────────
POC mode : reads CSVs from /input, snapshots into Git repo,
           commits and pushes to GitHub.

Folder structure in GitHub:
  prod/
    YYYY-MM-DD_HH-MM-SS/
      ExtractionRequest.csv
      DynamicTable.csv
      ...

Run manually : python tracker.py
Schedule it  : Windows Task Scheduler
────────────────────────────────────────────────────────────────
"""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import config


def log(msg):
    print(msg, flush=True)


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"STDERR: {result.stderr.strip()}"
        )
    return result.stdout.strip()


# ── Git ──────────────────────────────────────────────────────────

def ensure_git_repo(repo_path):
    repo_path.mkdir(parents=True, exist_ok=True)
    if not (repo_path / ".git").exists():
        log("  → Initialising new Git repo in snapshots/")
        run(["git", "init", "-b", "main"], cwd=str(repo_path))
        run(["git", "config", "user.name",  config.GIT_USER_NAME],  cwd=str(repo_path))
        run(["git", "config", "user.email", config.GIT_USER_EMAIL], cwd=str(repo_path))
        run(["git", "remote", "add", "origin", config.GITHUB_REMOTE], cwd=str(repo_path))
        log(f"  → Remote: {config.GITHUB_REMOTE}")


def git_commit_and_push(repo_path, timestamp, files):
    run(["git", "add", "-A"], cwd=str(repo_path))
    status = run(["git", "status", "--porcelain"], cwd=str(repo_path))
    if not status:
        log("  ✓  No changes detected — already up to date.")
        return False
    msg = f"snapshot: {config.ENVIRONMENT} — {timestamp} ({len(files)} file(s))"
    run(["git", "commit", "-m", msg], cwd=str(repo_path))
    log(f"  → Committed: {msg}")
    run(["git", "pull", "--rebase", "origin", "main"], cwd=str(repo_path))
    run(["git", "push", "--set-upstream", "origin", "main"], cwd=str(repo_path))
    log("  ✓  Pushed to GitHub.")
    return True


# ── CSV mode ─────────────────────────────────────────────────────

def collect_from_input(input_path, snapshot_path):
    csv_files = list(input_path.glob("*.csv"))
    if not csv_files:
        log("  ⚠  No CSV files found in input/ — nothing to snapshot.")
        return []
    snapshot_path.mkdir(parents=True, exist_ok=True)
    collected = []
    for f in csv_files:
        shutil.copy2(f, snapshot_path / f.name)
        log(f"  → Copied: {f.name}")
        collected.append(f)
    return collected


# ── DB mode ──────────────────────────────────────────────────────

def collect_from_db(queries_path, snapshot_path):
    try:
        import pyodbc, csv as csv_module
    except ImportError:
        raise RuntimeError("pyodbc not installed. Run: pip install pyodbc")

    sql_files = list(queries_path.glob("*.sql"))
    if not sql_files:
        log("  ⚠  No .sql files found in queries/")
        return []

    snapshot_path.mkdir(parents=True, exist_ok=True)
    log(f"  → Connecting to {config.DB_TYPE} database...")
    conn   = pyodbc.connect(config.DB_CONNECTION_STRING)
    cursor = conn.cursor()
    collected = []

    for sql_file in sql_files:
        out = snapshot_path / f"{sql_file.stem}.csv"
        try:
            cursor.execute(sql_file.read_text(encoding='utf-8').strip())
            rows    = cursor.fetchall()
            headers = [col[0] for col in cursor.description]
            with open(out, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv_module.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            log(f"  → {sql_file.name} → {len(rows)} rows")
            collected.append(out)
        except Exception as e:
            log(f"  ⚠  Failed: {sql_file.name} — {e}")

    cursor.close()
    conn.close()
    return collected


# ── Archive ───────────────────────────────────────────────────────

def archive_input(files, processed_path, timestamp):
    processed_path.mkdir(exist_ok=True)
    for f in files:
        shutil.move(str(f), processed_path / f"{f.stem}_{timestamp}{f.suffix}")
        log(f"  → Archived: {f.name}")


# ── Main ──────────────────────────────────────────────────────────

def main():
    now       = datetime.today()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    log(f"\n{'─'*55}")
    log(f"  MX Config Tracker  |  {now.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  Environment        |  {config.ENVIRONMENT}")
    log(f"  Mode               |  {config.MODE}")
    log(f"{'─'*55}\n")

    base_path      = Path(__file__).parent
    input_path     = base_path / config.INPUT_FOLDER
    repo_path      = base_path / "snapshots"
    processed_path = base_path / "processed"
    snapshot_path  = repo_path / config.ENVIRONMENT / timestamp

    input_path.mkdir(exist_ok=True)

    log("[1/3] Checking Git repo...")
    ensure_git_repo(repo_path)

    if config.MODE == "csv":
        log(f"\n[2/3] CSV mode → reading from input/")
        collected = collect_from_input(input_path, snapshot_path)
    elif config.MODE == "db":
        queries_path = base_path / "queries"
        queries_path.mkdir(exist_ok=True)
        log(f"\n[2/3] DB mode → running queries/")
        collected = collect_from_db(queries_path, snapshot_path)
    else:
        log(f"  ✗  Unknown MODE '{config.MODE}'")
        sys.exit(1)

    if not collected:
        sys.exit(0)

    log(f"\n[3/3] Pushing to GitHub...")
    pushed = git_commit_and_push(repo_path, timestamp, collected)

    if pushed and config.MODE == "csv":
        log(f"\n[+] Archiving → processed/")
        archive_input(collected, processed_path, timestamp)

    log(f"\n✅  Done — {len(collected)} file(s) pushed to GitHub\n")


if __name__ == "__main__":
    main()
