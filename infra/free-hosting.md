# Free public hosting for the dev box

## Current setup: Cloudflare quick tunnels (no account, free)

The machine has a public IP (20.166.120.83, Azure) but **all inbound ports are
blocked** by the Azure network security group + Windows Firewall (no admin
rights), so direct sslip.io hosting is impossible from inside the VM.

Quick tunnels punch out instead:

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

## Switching to sslip.io (when you control the Azure NSG)

sslip.io is just DNS: `20.166.120.83.sslip.io` already resolves to this VM.
To serve on it you need inbound ports open:

1. Azure portal → the VM's Network Security Group → add inbound rules for
   TCP 80 + 443.
2. On the VM (as admin):
   `New-NetFirewallRule -DisplayName Web -Direction Inbound -Protocol TCP -LocalPort 80,443 -Action Allow`
3. Run [Caddy](https://caddyserver.com) as the front door — it gets free
   Let's Encrypt certificates automatically:

   ```
   # Caddyfile
   app.20.166.120.83.sslip.io {
       reverse_proxy localhost:3000
   }
   api.20.166.120.83.sslip.io {
       reverse_proxy localhost:8800
   }
   ```

4. Set `NEXT_PUBLIC_API_URL=https://api.20.166.120.83.sslip.io`,
   add `.sslip.io` to `ALLOWED_HOSTS` (already done), restart both apps.

Stable URLs, real HTTPS, still $0 — but it needs the NSG change first.
