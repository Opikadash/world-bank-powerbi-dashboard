# setup.ps1 - PowerShell Script to Set Up World Bank Data Analysis Project (Windows)

Write-Host "🔧 Starting setup for World Bank Data Analysis Project..." -ForegroundColor Cyan

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.8+ and re-run this script." -ForegroundColor Red
    exit
}

# Step 1: Create virtual environment
Write-Host "`n📁 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Step 2: Activate the virtual environment
Write-Host "✅ Virtual environment created. Activating it..." -ForegroundColor Green
. .\venv\Scripts\Activate.ps1

# Step 3: Install dependencies
Write-Host "`n📦 Installing required Python packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Create data and output folders if not exist
Write-Host "`n📂 Creating folder structure..." -ForegroundColor Yellow
$folders = @("data", "outputs", "notebooks", "powerbi/screenshots")
foreach ($folder in $folders) {
    if (-not (Test-Path -Path $folder)) {
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        Write-Host "✔ Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "✔ Exists: $folder" -ForegroundColor Gray
    }
}

# Step 5: Initial message
Write-Host "`n✅ Setup complete. You can now run your scripts and open the Power BI dashboard." -ForegroundColor Cyan
Write-Host "To activate your environment in future sessions, run:" -ForegroundColor Yellow
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor White
