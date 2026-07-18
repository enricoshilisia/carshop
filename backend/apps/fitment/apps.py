from django.apps import AppConfig


class FitmentConfig(AppConfig):
    name = "apps.fitment"
    verbose_name = "Fitment"

    def ready(self):
        from apps.fitment import signals  # noqa: F401
