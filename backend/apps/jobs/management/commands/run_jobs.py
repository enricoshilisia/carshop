"""Claims one job at a time and exits cleanly before the host kills it.

MySQL 8 / MariaDB 10.6 support skip_locked, so overlapping cron ticks are
safe. SQLite (dev) serialises writes anyway.

cPanel cron:
    */5 * * * * cd ~/app && ~/venv/bin/python manage.py run_jobs --max-seconds=240
"""
import time
import traceback

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from apps.jobs.handlers import REGISTRY
from apps.jobs.models import Job


class Command(BaseCommand):
    help = "Process queued jobs until the queue is empty or --max-seconds elapses."

    def add_arguments(self, parser):
        parser.add_argument("--max-seconds", type=int, default=240)

    def handle(self, *args, **opts):
        deadline = time.monotonic() + opts["max_seconds"]
        processed = 0
        while time.monotonic() < deadline:
            job = self._claim()
            if not job:
                break
            self._run(job, deadline)
            processed += 1
        self.stdout.write(f"run_jobs: processed {processed} job(s)")

    def _claim(self):
        with transaction.atomic():
            qs = Job.objects.filter(status="queued", run_after__lte=timezone.now()).order_by(
                "priority", "id"
            )
            if connection.features.has_select_for_update_skip_locked:
                qs = qs.select_for_update(skip_locked=True)
            job = qs.first()
            if not job:
                return None
            job.status = "running"
            job.attempts += 1
            job.save(update_fields=["status", "attempts"])
            return job

    def _run(self, job, deadline):
        fn = REGISTRY.get(job.name)
        try:
            if fn is None:
                raise ValueError(f"No handler registered for job '{job.name}'")
            fn(job, lambda: time.monotonic() < deadline)
            job.status = "done"
            job.error = ""
        except Exception:
            job.error = traceback.format_exc()[-4000:]
            job.status = "failed" if job.attempts >= 3 else "queued"
            self.stderr.write(f"job {job.pk} ({job.name}) errored (attempt {job.attempts})")
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error", "finished_at"])
