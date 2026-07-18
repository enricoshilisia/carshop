"""Job handlers. Any handler that could touch >500 rows MUST checkpoint into
job.cursor, re-queue itself, and return — a job that runs to completion in one
tick on a big dataset is a job that gets the account flagged.
"""
from apps.jobs.models import Job, enqueue

REGISTRY = {}


def handler(name):
    def wrap(fn):
        REGISTRY[name] = fn
        return fn

    return wrap


@handler("rebuild_generation")
def rebuild_generation(job: Job, deadline_check):
    from apps.fitment.services import rebuild_generation as run

    gen_id = job.payload["generation_id"]
    remaining = job.cursor.get("remaining")
    remaining = run(gen_id, product_ids=remaining, chunk=200)
    if remaining:
        # Checkpoint and re-queue instead of blowing the cron tick.
        follow_up = enqueue(
            "rebuild_generation",
            {"generation_id": gen_id},
            dedupe_key=f"rebuild_generation:{gen_id}:cont:{len(remaining)}",
        )
        if follow_up:
            follow_up.cursor = {"remaining": remaining}
            follow_up.save(update_fields=["cursor"])


@handler("rebuild_product")
def rebuild_product(job: Job, deadline_check):
    from apps.catalog.models import Product
    from apps.fitment.services import rebuild_product_index

    product = Product.objects.filter(id=job.payload["product_id"]).first()
    if product:
        rebuild_product_index(product)


@handler("rebuild_all_search_docs")
def rebuild_all_search_docs(job: Job, deadline_check):
    from apps.catalog.models import Product
    from apps.catalog.search import rebuild_search_doc

    last_id = job.cursor.get("last_id", 0)
    batch = list(
        Product.objects.filter(id__gt=last_id).order_by("id")[:200]
    )
    for p in batch:
        rebuild_search_doc(p)
    if len(batch) == 200:
        follow_up = enqueue(
            "rebuild_all_search_docs",
            dedupe_key=f"rebuild_all_search_docs:{batch[-1].id}",
        )
        if follow_up:
            follow_up.cursor = {"last_id": batch[-1].id}
            follow_up.save(update_fields=["cursor"])
