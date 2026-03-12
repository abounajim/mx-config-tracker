# Config Tracker

Reads CSV query outputs, snapshots them daily into a Git repo, and pushes to Bitbucket — so you can compare config changes between any two dates.

---

## Folder structure

```
config-tracker/
├── input/              ← drop your CSVs here each day
├── snapshots/          ← auto-created Git repo (don't touch)
├── config.py           ← your settings
├── tracker.py          ← main script
└── README.md
```

---

## Setup (one-time)

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```
*(No external libraries needed right now — only stdlib)*

### 2. Edit config.py
Fill in:
- `BITBUCKET_REMOTE` — your Bitbucket repo URL
- `GIT_USER_NAME` / `GIT_USER_EMAIL`
- `ENVIRONMENT` — leave as "prod" for now

### 3. Create the Bitbucket repo
Create an **empty** repo in Bitbucket (no README, no .gitignore).
Copy its clone URL into `BITBUCKET_REMOTE` in config.py.

### 4. Test it manually
Drop some CSVs into `input/` and run:
```bash
python tracker.py
```
Check Bitbucket — you should see a commit with today's date.

---

## Daily scheduling

### Windows (Task Scheduler)
1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily, set your preferred time (e.g. 7:00 AM)
3. Action: Start a program
   - Program: `python`
   - Arguments: `tracker.py`
   - Start in: `C:\path\to\config-tracker`

### Mac/Linux (cron)
```bash
crontab -e
# Run every day at 7:00 AM:
0 7 * * * cd /path/to/config-tracker && python tracker.py >> logs/tracker.log 2>&1
```

---

## How to compare changes in Bitbucket

1. Open your Bitbucket repo
2. Go to **Commits** — each day is one commit
3. Click any commit to see exactly which CSV rows changed
4. Or use **Branches → Compare** to diff two specific dates

---

## Roadmap
- [ ] Connect directly to Murex DB (replace CSV drop with live queries)
- [ ] Add tst01 / tst02 environments
- [ ] Email/Slack alert when changes are detected
