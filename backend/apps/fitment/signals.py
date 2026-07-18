"""One product / its fitments saved → rebuild INLINE (milliseconds).
A variant or generation edit → QUEUED (touches every product on the generation).
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.fitment.models import Fitment
from apps.fitment.services import rebuild_product_index
from apps.jobs.models import enqueue
from apps.vehicles.models import VehicleGeneration, VehicleVariant


@receiver(post_save, sender=Fitment)
@receiver(post_delete, sender=Fitment)
def fitment_changed(sender, instance, **kwargs):
    rebuild_product_index(instance.product)


@receiver(post_save, sender=VehicleVariant)
@receiver(post_delete, sender=VehicleVariant)
def variant_changed(sender, instance, **kwargs):
    enqueue(
        "rebuild_generation",
        {"generation_id": instance.generation_id},
        dedupe_key=f"rebuild_generation:{instance.generation_id}",
    )


@receiver(post_save, sender=VehicleGeneration)
def generation_changed(sender, instance, created, **kwargs):
    if not created:
        enqueue(
            "rebuild_generation",
            {"generation_id": instance.id},
            dedupe_key=f"rebuild_generation:{instance.id}",
        )
