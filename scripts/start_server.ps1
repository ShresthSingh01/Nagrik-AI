param (
    [switch]$SkipInstall,
    [switch]$NoReload,
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1"
)

Write-Host "--- Nagrik-AI Bootstrapper ---" -ForegroundColor Cyan

# 1. Ensure Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Activate Venv
$ActivateScript = Join-Path (Get-Location) ".venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
} else {
    Write-Error "Could not find activation script at $ActivateScript"
    exit 1
}

# 3. Install Dependencies
if (-not $SkipInstall) {
    Write-Host "[*] Checking dependencies..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt
}

# 4. Check Environment File
if (-not (Test-Path ".env")) {
    Write-Host "[!] .env missing. Copying from .env.example..." -ForegroundColor Magenta
    Copy-Item ".env.example" ".env"
}

# 5. Start Server
$ReloadFlag = if ($NoReload) { "" } else { "--reload" }
Write-Host "[*] Starting FastAPI on http://$BindHost:$Port" -ForegroundColor Green
python -m uvicorn backend.main:app --host $BindHost --port $Port $ReloadFlag
