"""Seed fixture — real Kenya vehicles + a demo catalog with fitment rules.

Idempotent: safe to run twice (everything is get_or_create keyed on slugs/SKUs).
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Offer, PartNumber, Product
from apps.fitment.models import Fitment
from apps.vehicles.models import (
    OPEN_YEAR,
    VehicleEngine,
    VehicleGeneration,
    VehicleMake,
    VehicleModel,
    VehicleModelAlias,
    VehicleTrim,
    VehicleVariant,
)

# make, model, aliases, [(gen code, slug, yf, yt, body, trims, engines, variant years)]
VEHICLES = [
    ("Toyota", "toyota", "Land Cruiser Prado", "land-cruiser-prado", ["Prado", "LC Prado"], [
        ("J120", "j120", 2002, 2009, "SUV", ["TX", "VX"],
         [("2.7L Petrol", "2TR-FE", "2-7-petrol-2tr-fe", "petrol", 2694),
          ("3.0L Diesel", "1KD-FTV", "3-0-diesel-1kd-ftv", "diesel", 2982)]),
        ("J150", "j150", 2009, 2023, "SUV", ["TX", "TX-L", "VX"],
         [("2.8L Diesel", "1GD-FTV", "2-8-diesel-1gd-ftv", "diesel", 2755),
          ("4.0L Petrol", "1GR-FE", "4-0-petrol-1gr-fe", "petrol", 3956)]),
    ]),
    ("Toyota", "toyota", "Harrier", "harrier", ["Harrier"], [
        ("XU60", "xu60", 2013, 2020, "SUV", ["Elegance", "Premium"],
         [("2.0L Petrol", "3ZR-FAE", "2-0-petrol-3zr-fae", "petrol", 1986)]),
        ("XU80", "xu80", 2020, OPEN_YEAR, "SUV", ["G", "Z"],
         [("2.0L Petrol", "M20A-FKS", "2-0-petrol-m20a-fks", "petrol", 1987)]),
    ]),
    ("Toyota", "toyota", "Hilux", "hilux", ["Hilux"], [
        ("GUN125", "gun125", 2015, OPEN_YEAR, "Pickup", ["Single Cab", "Double Cab"],
         [("2.4L Diesel", "2GD-FTV", "2-4-diesel-2gd-ftv", "diesel", 2393)]),
    ]),
    ("Toyota", "toyota", "Vitz", "vitz", ["Vitz", "Yaris"], [
        ("XP130", "xp130", 2010, 2020, "Hatchback", ["F", "Jewela"],
         [("1.3L Petrol", "1NR-FE", "1-3-petrol-1nr-fe", "petrol", 1329)]),
    ]),
    ("Toyota", "toyota", "Corolla Fielder", "corolla-fielder", ["Fielder"], [
        ("E160", "e160", 2012, OPEN_YEAR, "Wagon", ["X", "G"],
         [("1.5L Petrol", "1NZ-FE", "1-5-petrol-1nz-fe", "petrol", 1496)]),
    ]),
    ("Toyota", "toyota", "Corolla Axio", "corolla-axio", ["Axio"], [
        ("E160", "e160", 2012, OPEN_YEAR, "Sedan", ["X", "G"],
         [("1.5L Petrol", "1NZ-FE", "1-5-petrol-1nz-fe", "petrol", 1496)]),
    ]),
    ("Toyota", "toyota", "Premio", "premio", ["Premio"], [
        ("T260", "t260", 2007, 2021, "Sedan", ["F", "G"],
         [("1.8L Petrol", "2ZR-FAE", "1-8-petrol-2zr-fae", "petrol", 1797)]),
    ]),
    ("Toyota", "toyota", "Probox", "probox", ["Probox"], [
        ("XP160", "xp160", 2014, OPEN_YEAR, "Van", ["DX", "GL"],
         [("1.5L Petrol", "1NZ-FE", "1-5-petrol-1nz-fe", "petrol", 1496)]),
    ]),
    ("Mazda", "mazda", "CX-5", "cx-5", ["CX5"], [
        ("KF", "kf", 2017, OPEN_YEAR, "SUV", ["20S", "25S"],
         [("2.0L Petrol", "PE-VPS", "2-0-petrol-pe-vps", "petrol", 1998),
          ("2.2L Diesel", "SH-VPTS", "2-2-diesel-sh-vpts", "diesel", 2191)]),
    ]),
    ("Mazda", "mazda", "Demio", "demio", ["Demio", "Mazda2"], [
        ("DJ", "dj", 2014, 2023, "Hatchback", ["13C", "15C"],
         [("1.3L Petrol", "P3-VPS", "1-3-petrol-p3-vps", "petrol", 1298)]),
    ]),
    ("Nissan", "nissan", "Note", "note", ["Note"], [
        ("E12", "e12", 2012, 2020, "Hatchback", ["S", "Medalist"],
         [("1.2L Petrol", "HR12DDR", "1-2-petrol-hr12ddr", "petrol", 1198)]),
    ]),
]

# name, slug, kind, google category
CATEGORIES = [
    ("Brake Pads", "brake-pads", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Braking"),
    ("Brake Discs", "brake-discs", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Braking"),
    ("Oil Filters", "oil-filters", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Engine Filters"),
    ("Air Filters", "air-filters", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Engine Filters"),
    ("Shock Absorbers", "shock-absorbers", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Suspension"),
    ("Spark Plugs", "spark-plugs", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Ignition"),
    ("Wiper Blades", "wiper-blades", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts"),
    ("Batteries", "batteries", "vehicle", "Vehicle Parts & Accessories > Vehicle Parts > Electrical"),
    ("Laptops", "laptops", "general", "Electronics > Computers > Laptops"),
]

BRANDS = [
    ("Brembo", "brembo", False), ("Bosch", "bosch", False), ("Denso", "denso", False),
    ("Toyota Genuine", "toyota-genuine", True), ("KYB", "kyb", False), ("NGK", "ngk", False),
    ("Mann-Filter", "mann-filter", False), ("Chloride Exide", "chloride-exide", False),
]


class Command(BaseCommand):
    help = "Seed demo vehicles, categories, brands, products and fitment."

    def handle(self, *args, **opts):
        makes, gens, trims, engines = {}, {}, {}, {}

        for make_name, make_slug, model_name, model_slug, aliases, generations in VEHICLES:
            make, _ = VehicleMake.objects.get_or_create(
                slug=make_slug, defaults={"name": make_name, "popularity": 100 if make_slug == "toyota" else 50}
            )
            model, _ = VehicleModel.objects.get_or_create(
                make=make, slug=model_slug, defaults={"name": model_name}
            )
            for alias in aliases:
                VehicleModelAlias.objects.get_or_create(model=model, alias=alias)
            for code, gslug, yf, yt, body, trim_names, engine_rows in generations:
                gen, _ = VehicleGeneration.objects.get_or_create(
                    model=model, slug=gslug,
                    defaults={"code": code, "year_from": yf, "year_to": yt, "body_type": body},
                )
                gens[(model_slug, gslug)] = gen
                gen_trims, gen_engines = [], []
                for tname in trim_names:
                    trim, _ = VehicleTrim.objects.get_or_create(
                        generation=gen, slug=tname.lower().replace(" ", "-"), defaults={"name": tname}
                    )
                    gen_trims.append(trim)
                for display, ecode, eslug, fuel, cc in engine_rows:
                    eng, _ = VehicleEngine.objects.get_or_create(
                        generation=gen, slug=eslug,
                        defaults={"display": display, "code": ecode, "fuel": fuel, "capacity_cc": cc},
                    )
                    gen_engines.append(eng)
                trims[(model_slug, gslug)] = gen_trims
                engines[(model_slug, gslug)] = gen_engines
                # Variants: trim × engine over the generation's years.
                for trim in gen_trims:
                    for eng in gen_engines:
                        VehicleVariant.objects.get_or_create(
                            generation=gen, trim=trim, engine=eng,
                            year_from=gen.year_from, year_to=gen.year_to,
                            defaults={"market": "KE"},
                        )

        cats = {}
        for name, slug, kind, gcat in CATEGORIES:
            existing = Category.objects.filter(slug=slug).first()
            if existing:
                cats[slug] = existing
            else:
                cats[slug] = Category.add_root(
                    name=name, slug=slug, kind=kind, google_category=gcat
                )

        brands = {}
        for name, slug, is_oem in BRANDS:
            brands[slug], _ = Brand.objects.get_or_create(
                slug=slug, defaults={"name": name, "is_oem": is_oem}
            )

        # sku, brand, category, name, mpn, price, oem numbers, fitments
        # fitment: (model_slug, gen_slug, trim_idx|None, engine_idx|None, yf, yt, position, is_exclusion)
        products = [
            ("BRM-P83145", "brembo", "brake-pads", "Brembo P83-145 Front Brake Pads", "P83-145",
             14500, ["04465-60280"],
             [("land-cruiser-prado", "j150", None, None, 2015, 2023, "front", False)]),
            ("TGN-0446560320", "toyota-genuine", "brake-pads", "Toyota Genuine Front Brake Pads Prado J150", "04465-60320",
             18900, ["04465-60320"],
             [("land-cruiser-prado", "j150", None, None, 2009, 2023, "front", False)]),
            ("BSH-0986AB1234", "bosch", "brake-pads", "Bosch Front Brake Pads Harrier", "0986AB1234",
             7800, ["04465-48150"],
             [("harrier", "xu60", None, None, 2013, 2020, "front", False),
              ("harrier", "xu80", None, None, 2020, OPEN_YEAR, "front", False)]),
            ("BRM-09A86311", "brembo", "brake-discs", "Brembo 09.A863.11 Front Brake Discs Pair", "09.A863.11",
             22500, ["43512-60180"],
             [("land-cruiser-prado", "j150", None, None, 2009, 2023, "front", False)]),
            ("MNF-W7124", "mann-filter", "oil-filters", "Mann-Filter W 712/4 Oil Filter", "W 712/4",
             1450, ["90915-YZZE1"],
             [("vitz", "xp130", None, None, 2010, 2020, "", False),
              ("corolla-fielder", "e160", None, None, 2012, OPEN_YEAR, "", False),
              ("corolla-axio", "e160", None, None, 2012, OPEN_YEAR, "", False),
              ("probox", "xp160", None, None, 2014, OPEN_YEAR, "", False)]),
            ("DNS-1109050", "denso", "oil-filters", "Denso Oil Filter Hilux 2.4 Diesel", "110905-0",
             2100, ["90915-YZZD4"],
             [("hilux", "gun125", None, None, 2015, OPEN_YEAR, "", False)]),
            ("BSH-F026400374", "bosch", "air-filters", "Bosch F026400374 Air Filter CX-5", "F026400374",
             3200, ["PE07-13-3A0"],
             [("cx-5", "kf", None, None, 2017, OPEN_YEAR, "", False)]),
            ("KYB-349041", "kyb", "shock-absorbers", "KYB Excel-G 349041 Rear Shock Absorber", "349041",
             8900, ["48531-60820"],
             # Fits the whole Prado J150 range EXCEPT the 4.0 petrol engine (demo exclusion).
             [("land-cruiser-prado", "j150", None, None, 2009, 2023, "rear", False),
              ("land-cruiser-prado", "j150", None, 1, 2009, 2023, "rear", True)]),
            ("NGK-ILKAR7B11", "ngk", "spark-plugs", "NGK ILKAR7B11 Laser Iridium Spark Plug", "ILKAR7B11",
             1850, ["90919-01247"],
             [("corolla-fielder", "e160", None, None, 2012, OPEN_YEAR, "", False),
              ("corolla-axio", "e160", None, None, 2012, OPEN_YEAR, "", False),
              ("note", "e12", None, None, 2012, 2020, "", False)]),
            ("DNS-DW6045", "denso", "wiper-blades", "Denso Hybrid Wiper Blade 600mm", "DW60-45",
             1200, [], "universal"),
            ("CHL-N70MF", "chloride-exide", "batteries", "Chloride Exide N70MF Maintenance-Free Battery", "N70MF",
             13500, [],
             [("land-cruiser-prado", "j120", None, None, 2002, 2009, "", False),
              ("land-cruiser-prado", "j150", None, None, 2009, 2023, "", False),
              ("hilux", "gun125", None, None, 2015, OPEN_YEAR, "", False)]),
            ("KYB-339031", "kyb", "shock-absorbers", "KYB Excel-G 339031 Front Shock Absorber Demio", "339031",
             7200, ["D651-34-700"],
             [("demio", "dj", None, None, 2014, 2023, "front", False)]),
        ]

        created = 0
        for row in products:
            sku, brand_slug, cat_slug, name, mpn, price, oem_numbers, fit_spec = row
            slug = name.lower().replace(" ", "-").replace(".", "-").replace("/", "-")
            product, was_created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "brand": brands[brand_slug],
                    "category": cats[cat_slug],
                    "name": name,
                    "slug": slug,
                    "mpn": mpn,
                    "description": f"{name}. Quality-assured with verified vehicle fitment, delivered across Kenya.",
                    "is_universal": fit_spec == "universal",
                },
            )
            if was_created:
                created += 1
            Offer.objects.get_or_create(
                product=product,
                defaults={"price": Decimal(price), "stock_qty": 25, "availability": "in_stock"},
            )
            for number in oem_numbers:
                PartNumber.objects.get_or_create(
                    product=product, number=number, defaults={"kind": "oem"}
                )
            if fit_spec != "universal":
                for model_slug, gen_slug, trim_idx, engine_idx, yf, yt, position, is_excl in fit_spec:
                    gen = gens[(model_slug, gen_slug)]
                    Fitment.objects.get_or_create(
                        product=product,
                        generation=gen,
                        trim=trims[(model_slug, gen_slug)][trim_idx] if trim_idx is not None else None,
                        engine=engines[(model_slug, gen_slug)][engine_idx] if engine_idx is not None else None,
                        year_from=yf,
                        year_to=yt,
                        position=position,
                        is_exclusion=is_excl,
                        defaults={"source": "manual", "confidence": 1.0},
                    )
            # Signals rebuilt the index on each save; force one clean final pass.
            from apps.fitment.services import rebuild_product_index

            rebuild_product_index(product)

        self.stdout.write(self.style.SUCCESS(
            f"seed_demo: {VehicleVariant.objects.count()} variants, "
            f"{Product.objects.count()} products ({created} new)"
        ))
