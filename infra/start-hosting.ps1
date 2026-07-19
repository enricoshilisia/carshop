# Brings the whole stack up after a reboot: Django + Next + Caddy (sslip.io HTTPS).
# Usage:  powershell -ExecutionPolicy Bypass -File infra\start-hosting.ps1
$repo = Split-Path $PSScriptRoot -Parent

# 1. Django API on :8800
$env:PYTHONIOENCODING = "utf-8"
Start-Process -WindowStyle Hidden -FilePath "$repo\backend\.venv\Scripts\python.exe" `
  -ArgumentList "manage.py", "runserver", "127.0.0.1:8800", "--noreload" `
  -WorkingDirectory "$repo\backend" `
  -RedirectStandardError "$repo\backend\runserver.err.log" `
  -RedirectStandardOutput "$repo\backend\runserver.out.log"

# 2. Next.js on :3000 — PRODUCTION server (run `npm run build` after code
# changes; NEXT_PUBLIC_API_URL must be set at build time, API_URL at runtime).
$env:API_URL = "http://localhost:8800"
$env:REVALIDATE_SECRET = "dev-revalidate-secret"
Start-Process -WindowStyle Hidden -FilePath "cmd.exe" `
  -ArgumentList "/c", "npm run start > next-server.log 2>&1" `
  -WorkingDirectory "$repo\frontend"

# 3. Caddy on :80/:443 — HTTPS for app./api.20.166.120.83.sslip.io
Start-Process -WindowStyle Hidden -FilePath "$env:LOCALAPPDATA\caddy\caddy.exe" `
  -ArgumentList "run", "--config", "$repo\infra\Caddyfile" `
  -RedirectStandardError "$env:LOCALAPPDATA\caddy\caddy.log" `
  -RedirectStandardOutput "$env:LOCALAPPDATA\caddy\caddy.out.log"

Start-Sleep -Seconds 12
try {
  $code = (Invoke-WebRequest -UseBasicParsing "https://app.20.166.120.83.sslip.io/" -TimeoutSec 60).StatusCode
  Write-Host "Site is LIVE: https://app.20.166.120.83.sslip.io ($code)"
} catch {
  Write-Host "Startup check failed: $($_.Exception.Message) - check the log files."
}
