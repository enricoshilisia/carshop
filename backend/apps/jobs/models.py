from datetime import timedelta

from django.db import models
from django.utils import timezone

STATUS = [
    ("queued", "Queued"),
    ("running", "Running"),
    ("done", "Done"),
    ("failed", "Failed"),
]


class Job(models.Model):
    """DB-backed job queue. Cron runs `manage.py run_jobs` every 5 minutes."""

    name = models.CharField(max_length=64)  # e.g. "rebuild_generation"
    payload = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=200, blank=True, db_index=True)
    status = models.CharField(max_length=12, default="queued", db_index=True, choices=STATUS)
    priority = models.SmallIntegerField(default=5)
    run_after = models.DateTimeField(default=timezone.now, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    cursor = models.JSONField(default=dict, blank=True)  # resume point for chunked jobs
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["priority", "id"]

    def __str__(self):
        return f"{self.name} #{self.pk} ({self.status})"


def enqueue(name, payload=None, dedupe_key="", priority=5, delay=0):
    """dedupe_key stops 500 identical rebuild jobs from one bulk edit."""
    if dedupe_key and Job.objects.filter(dedupe_key=dedupe_key, status="queued").exists():
        return None
    return Job.objects.create(
        name=name,
        payload=payload or {},
        dedupe_key=dedupe_key,
        priority=priority,
        run_after=timezone.now() + timedelta(seconds=delay),
    )
