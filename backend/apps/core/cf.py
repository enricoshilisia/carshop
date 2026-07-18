"""Cloudflare purge-by-URL. Batched, fire-and-forget — never blocks a request."""
import logging
import threading

import requests
from django.conf import settings

log = logging.getLogger(__name__)

PURGE_ENDPOINT = "https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache"
BATCH = 30  # Cloudflare max URLs per purge call


def purge(urls: list[str]) -> None:
    """Purge absolute URLs from the Cloudflare edge cache, in the background."""
    if not settings.CLOUDFLARE_ZONE_ID or not settings.CLOUDFLARE_API_TOKEN or not urls:
        return
    threading.Thread(target=_purge_sync, args=(list(urls),), daemon=True).start()


def _purge_sync(urls: list[str]) -> None:
    endpoint = PURGE_ENDPOINT.format(zone=settings.CLOUDFLARE_ZONE_ID)
    headers = {"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"}
    for i in range(0, len(urls), BATCH):
        try:
            requests.post(endpoint, headers=headers, json={"files": urls[i : i + BATCH]}, timeout=10)
        except requests.RequestException as exc:
            log.warning("Cloudflare purge failed: %s", exc)


def purge_everything() -> None:
    """Full zone purge — justified only right after a frontend deploy."""
    if not settings.CLOUDFLARE_ZONE_ID or not settings.CLOUDFLARE_API_TOKEN:
        return
    endpoint = PURGE_ENDPOINT.format(zone=settings.CLOUDFLARE_ZONE_ID)
    headers = {"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"}
    try:
        requests.post(endpoint, headers=headers, json={"purge_everything": True}, timeout=15)
    except requests.RequestException as exc:
        log.warning("Cloudflare full purge failed: %s", exc)
