"""Seed the FULL vehicle taxonomy + parts category tree for the Kenya market.

Covers every vehicle type: cars, SUVs, pickups, vans, wagons, trucks, buses
and motorcycles — ~20 makes, real generation codes, trims and engines.
Variants are created as trim x engine over each generation's year span.

Idempotent: everything is get_or_create keyed on slugs, safe to re-run after
editing apps/vehicles/seed_data.py. Images are left blank — add them in admin.

Typical flow:
    python manage.py seed_vehicles
    python manage.py run_jobs --max-seconds=240   # process queued index rebuilds
    python manage.py build_variant_groups
    python manage.py rebuild_seo_registry
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Category
from apps.vehicles.models import (
    VehicleEngine,
    VehicleGeneration,
    VehicleMake,
    VehicleModel,
    VehicleModelAlias,
    VehicleTrim,
    VehicleVariant,
)
from apps.vehicles.seed_data import CATEGORY_TREE, GENERAL_CATEGORY_TREE, MAKES


class Command(BaseCommand):
    help = "Seed all makes/models/generations/trims/engines/variants + the parts category tree."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-categories", action="store_true", help="Skip the category tree"
        )
        parser.add_argument(
            "--no-vehicles", action="store_true", help="Skip the vehicle taxonomy"
        )

    def handle(self, *args, **opts):
        counts = {"categories": 0, "makes": 0, "models": 0, "generations": 0,
                  "trims": 0, "engines": 0, "variants": 0}

        if not opts["no_categories"]:
            counts["categories"] = self._seed_categories()
        if not opts["no_vehicles"]:
            self._seed_vehicles(counts)

        self.stdout.write(self.style.SUCCESS(
            "seed_vehicles: "
            f"{counts['categories']} new categories | "
            f"{counts['makes']} new makes, {counts['models']} models, "
            f"{counts['generations']} generations, {counts['trims']} trims, "
            f"{counts['engines']} engines, {counts['variants']} variants"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"totals now: {VehicleMake.objects.count()} makes, "
            f"{VehicleModel.objects.count()} models, "
            f"{VehicleGeneration.objects.count()} generations, "
            f"{VehicleVariant.objects.count()} variants, "
            f"{Category.objects.count()} categories"
        ))
        self.stdout.write(
            "next: run_jobs --max-seconds=240, build_variant_groups, rebuild_seo_registry"
        )

    # ------------------------------------------------------------------ helpers

    def _seed_categories(self) -> int:
        created = 0

        def ensure_root(name, gpc, kind):
            nonlocal created
            slug = slugify(name)
            node = Category.objects.filter(slug=slug).first()
            if node is None:
                node = Category.add_root(
                    name=name, slug=slug, kind=kind, google_category=gpc
                )
                created += 1
            return node

        for name, gpc, children in CATEGORY_TREE:
            root = ensure_root(name, gpc, "vehicle")
            for child_name in children:
                child_slug = slugify(child_name)
                if not Category.objects.filter(slug=child_slug).exists():
                    root.refresh_from_db()  # treebeard path bookkeeping
                    root.add_child(
                        name=child_name, slug=child_slug, kind="vehicle",
                        google_category=gpc,
                    )
                    created += 1

        for name, gpc, children in GENERAL_CATEGORY_TREE:
            ensure_root(name, gpc, "general")

        return created

    def _seed_vehicles(self, counts: dict) -> None:
        for make_name, make_data in MAKES.items():
            make, was_new = VehicleMake.objects.get_or_create(
                slug=slugify(make_name),
                defaults={"name": make_name, "popularity": make_data["popularity"]},
            )
            counts["makes"] += was_new

            for model_name, model_data in make_data["models"].items():
                model, was_new = VehicleModel.objects.get_or_create(
                    make=make, slug=slugify(model_name), defaults={"name": model_name}
                )
                counts["models"] += was_new
                for alias in model_data.get("aliases", []):
                    VehicleModelAlias.objects.get_or_create(model=model, alias=alias)

                for code, yf, yt, body, trim_names, engine_rows in model_data["gens"]:
                    gen, was_new = VehicleGeneration.objects.get_or_create(
                        model=model, slug=slugify(code),
                        defaults={"code": code, "year_from": yf, "year_to": yt,
                                  "body_type": body},
                    )
                    counts["generations"] += was_new

                    trims = []
                    for trim_name in trim_names:
                        trim, was_new = VehicleTrim.objects.get_or_create(
                            generation=gen, slug=slugify(trim_name),
                            defaults={"name": trim_name},
                        )
                        counts["trims"] += was_new
                        trims.append(trim)

                    engines = []
                    for display, ecode, fuel, cc in engine_rows:
                        engine, was_new = VehicleEngine.objects.get_or_create(
                            generation=gen, slug=slugify(f"{display}-{ecode}"),
                            defaults={"display": display, "code": ecode,
                                      "fuel": fuel, "capacity_cc": cc},
                        )
                        counts["engines"] += was_new
                        engines.append(engine)

                    # The atomic sellable-against unit: trim x engine.
                    for trim in trims:
                        for engine in engines:
                            _, was_new = VehicleVariant.objects.get_or_create(
                                generation=gen, trim=trim, engine=engine,
                                year_from=gen.year_from, year_to=gen.year_to,
                                defaults={"market": "KE"},
                            )
                            counts["variants"] += was_new
