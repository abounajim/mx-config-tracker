# MX Config Tracker — build.ps1
# Run this once to package the app into a single .exe
# Requirements: Python 3.10+, pip

Write-Host "`n=== MX Config Tracker — Build Script ===" -ForegroundColor Cyan

# Install dependencies
Write-Host "`n[1/3] Installing dependencies..." -ForegroundColor Yellow
pip install pywebview pyinstaller --quiet

# Build exe
Write-Host "`n[2/3] Building exe..." -ForegroundColor Yellow
pyinstaller `
  --onefile `
  --noconsole `
  --name "MXConfigTracker" `
  --add-data "diff_viewer.html;." `
  --add-data "config.py;." `
  --icon NONE `
  app.py

# Copy config next to exe so client can edit it
Write-Host "`n[3/3] Copying config..." -ForegroundColor Yellow
Copy-Item config.py dist\config.py -Force

Write-Host "`n=== Done ===" -ForegroundColor Green
Write-Host "Deliverable: dist\MXConfigTracker.exe" -ForegroundColor Green
Write-Host "Give client: dist\MXConfigTracker.exe + dist\config.py`n" -ForegroundColor Green
