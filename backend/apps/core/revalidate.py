"""Notify the Next.js frontend to drop its ISR cache, then purge Cloudflare.

Order matters: purge the edge AFTER Next has revalidated, or Cloudflare
just re-caches the stale page.
"""
import logging
import threading

import requests
from django.conf import settings

from apps.core import cf

log = logging.getLogger(__name__)


def revalidate(paths: list[str] | None = None, tags: list[str] | None = None) -> None:
    if not paths and not tags:
        return
    threading.Thread(target=_revalidate_sync, args=(paths or [], tags or []), daemon=True).start()


def _revalidate_sync(paths: list[str], tags: list[str]) -> None:
    try:
        requests.post(
            f"{settings.SITE_BASE_URL}/api/revalidate",
            json={"paths": paths, "tags": tags, "secret": settings.REVALIDATE_SECRET},
            timeout=10,
        )
    except requests.RequestException as exc:
        log.warning("Next.js revalidate failed: %s", exc)
    cf._purge_sync([f"{settings.SITE_BASE_URL}{p}" for p in paths])
