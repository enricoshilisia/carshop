from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.catalog.models import Offer, PartNumber, Product
from apps.catalog.search import rebuild_search_doc


@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    from apps.fitment.services import rebuild_product_index

    rebuild_product_index(instance)
    rebuild_search_doc(instance)


@receiver(post_save, sender=PartNumber)
def part_number_saved(sender, instance, **kwargs):
    rebuild_search_doc(instance.product)


@receiver(post_save, sender=Offer)
def offer_saved(sender, instance, **kwargs):
    """Price/stock change → drop the Next.js ISR cache + Cloudflare, live <60s."""
    from apps.core.revalidate import revalidate

    revalidate(
        paths=[f"/products/{instance.product.slug}"],
        tags=[f"product:{instance.product_id}"],
    )
