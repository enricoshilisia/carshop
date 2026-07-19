# Free public hosting for the dev box

## ✅ Current setup: sslip.io + Caddy (live)

NSG ports 80/443 are open. Caddy terminates TLS with free Let's Encrypt
certificates and proxies to the local apps:

| Public URL | Proxies to |
|---|---|
| https://app.20.166.120.83.sslip.io | Next.js on :3000 |
| https://api.20.166.120.83.sslip.io | Django on :8800 |

- Config: `infra/Caddyfile` · binary: `%LOCALAPPDATA%\caddy\caddy.exe`
- Bring the whole stack up after a reboot: `powershell -File infra\start-hosting.ps1`
- Certs auto-renew as long as Caddy is running and 80/443 stay open.
- Frontend env split: `NEXT_PUBLIC_API_URL=https://api.20.166.120.83.sslip.io`
  (browser), `API_URL=http://localhost:8800` (server-side, fast local hop).

## Fallback: Cloudflare quick tunnels (no account, free)

If the NSG ever closes again, quick tunnels punch out instead:

```powershell
# API (Django on :8800)
& "$env:LOCALAPPDATA\cloudflared\cloudflared.exe" tunnel --url http://localhost:8800 --no-autoupdate
# Frontend (Next dev on :3000)
& "$env:LOCALAPPDATA\cloudflared\cloudflared.exe" tunnel --url http://localhost:3000 --no-autoupdate
```

Each prints a random `https://<words>.trycloudflare.com` URL. Then:

1. Backend `.env`: `ALLOWED_HOSTS` includes `.trycloudflare.com`; set
   `API_BASE_URL` to the API tunnel URL (used in feeds/JSON-LD).
2. Start Next with the split env:
   `NEXT_PUBLIC_API_URL=<api tunnel>` (browser) and
   `API_URL=http://localhost:8800` (server-side fetches stay local/fast).

**Caveats:** URLs change on every tunnel restart; tunnels die when the
machine sleeps. Demo-grade, not production.

## Notes

- sslip.io is just DNS: `anything.20.166.120.83.sslip.io` resolves to the VM.
  If the VM's public IP ever changes, update the Caddyfile hostnames and the
  frontend/backend env values to the new IP.
- This serves the DEV servers (runserver + next dev). Fine for demos; for
  real production traffic follow the cPanel/VPS deploy in BUILD_PLAN.md §9.
