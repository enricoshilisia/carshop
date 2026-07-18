"""Exit-gate tests: FitmentIndex must match a brute-force recomputation."""
from django.test import TestCase

from apps.catalog.models import Brand, Category, Offer, Product
from apps.fitment.models import Fitment, FitmentIndex
from apps.fitment.services import resolve_variants
from apps.vehicles.models import (
    OPEN_YEAR,
    VehicleEngine,
    VehicleGeneration,
    VehicleMake,
    VehicleModel,
    VehicleTrim,
    VehicleVariant,
)


def build_vehicle():
    make = VehicleMake.objects.create(name="Toyota", slug="toyota")
    model = VehicleModel.objects.create(make=make, name="Prado", slug="prado")
    gen = VehicleGeneration.objects.create(
        model=model, code="J150", slug="j150", year_from=2009, year_to=2023
    )
    tx = VehicleTrim.objects.create(generation=gen, name="TX", slug="tx")
    vx = VehicleTrim.objects.create(generation=gen, name="VX", slug="vx")
    diesel = VehicleEngine.objects.create(
        generation=gen, display="2.8L Diesel", code="1GD-FTV", slug="1gd", fuel="diesel"
    )
    petrol = VehicleEngine.objects.create(
        generation=gen, display="4.0L Petrol", code="1GR-FE", slug="1gr", fuel="petrol"
    )
    return make, model, gen, tx, vx, diesel, petrol


def build_product(sku="SKU-1", **kwargs):
    brand = Brand.objects.get_or_create(name="Brembo", slug="brembo")[0]
    cat = Category.objects.first() or Category.add_root(name="Brake Pads", slug="brake-pads", kind="vehicle")
    return Product.objects.create(
        sku=sku, brand=brand, category=cat, name=f"Part {sku}", slug=f"part-{sku.lower()}", **kwargs
    )


class ResolveVariantsTests(TestCase):
    def setUp(self):
        self.make, self.model, self.gen, self.tx, self.vx, self.diesel, self.petrol = build_vehicle()
        self.v_tx_diesel = VehicleVariant.objects.create(
            generation=self.gen, trim=self.tx, engine=self.diesel, year_from=2015, year_to=2023
        )
        self.v_tx_petrol = VehicleVariant.objects.create(
            generation=self.gen, trim=self.tx, engine=self.petrol, year_from=2009, year_to=2017
        )
        self.v_vx_diesel = VehicleVariant.objects.create(
            generation=self.gen, trim=self.vx, engine=self.diesel, year_from=2015, year_to=OPEN_YEAR
        )
        self.product = build_product()

    def test_year_overlap_inclusive(self):
        # Fitment 2018-2020 overlaps [2015,2023] and [2015,9999] but not [2009,2017]... wait, 2017 < 2018.
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2018, year_to=2020
        )
        ids = resolve_variants(self.product)
        self.assertEqual(ids, {self.v_tx_diesel.id, self.v_vx_diesel.id})

    def test_boundary_year_overlaps(self):
        # Single boundary year 2017 must still match [2009,2017] (inclusive edges).
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2017, year_to=2017
        )
        self.assertIn(self.v_tx_petrol.id, resolve_variants(self.product))

    def test_open_year_sentinel(self):
        # OPEN_YEAR variant matches a far-future fitment window.
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2030, year_to=2035
        )
        self.assertEqual(resolve_variants(self.product), {self.v_vx_diesel.id})

    def test_null_trim_is_wildcard(self):
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2009, year_to=OPEN_YEAR
        )
        self.assertEqual(len(resolve_variants(self.product)), 3)

    def test_trim_narrowing(self):
        Fitment.objects.create(
            product=self.product, generation=self.gen, trim=self.tx,
            year_from=2009, year_to=OPEN_YEAR,
        )
        self.assertEqual(
            resolve_variants(self.product), {self.v_tx_diesel.id, self.v_tx_petrol.id}
        )

    def test_exclusion_subtracted(self):
        # Fits whole generation EXCEPT the petrol engine.
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2009, year_to=OPEN_YEAR
        )
        Fitment.objects.create(
            product=self.product, generation=self.gen, engine=self.petrol,
            year_from=2009, year_to=OPEN_YEAR, is_exclusion=True,
        )
        self.assertEqual(
            resolve_variants(self.product), {self.v_tx_diesel.id, self.v_vx_diesel.id}
        )

    def test_universal_matches_everything(self):
        self.product.is_universal = True
        self.product.save()
        self.assertEqual(len(resolve_variants(self.product)), 3)

    def test_inactive_variant_excluded(self):
        self.v_tx_diesel.is_active = False
        self.v_tx_diesel.save()
        Fitment.objects.create(
            product=self.product, generation=self.gen, year_from=2009, year_to=OPEN_YEAR
        )
        self.assertNotIn(self.v_tx_diesel.id, resolve_variants(self.product))


class FitmentIndexPropertyTests(TestCase):
    """The exit gate: index rows == brute-force recomputation, always."""

    def setUp(self):
        self.make, self.model, self.gen, self.tx, self.vx, self.diesel, self.petrol = build_vehicle()
        for trim in (self.tx, self.vx):
            for engine in (self.diesel, self.petrol):
                for years in ((2009, 2013), (2013, 2017), (2017, OPEN_YEAR)):
                    VehicleVariant.objects.create(
                        generation=self.gen, trim=trim, engine=engine,
                        year_from=years[0], year_to=years[1],
                    )

    def brute_force(self, product):
        """O(n·m) reference implementation — no query tricks."""
        included, excluded = set(), set()
        for v in VehicleVariant.objects.filter(is_active=True):
            for f in product.fitments.all():
                matches = (
                    v.generation_id == f.generation_id
                    and f.year_from <= v.year_to
                    and v.year_from <= f.year_to
                    and (not f.trim_id or f.trim_id == v.trim_id)
                    and (not f.engine_id or f.engine_id == v.engine_id)
                    and (not f.drivetrain or f.drivetrain == v.drivetrain)
                )
                if matches:
                    (excluded if f.is_exclusion else included).add(v.id)
        return included - excluded

    def test_index_matches_brute_force(self):
        product = build_product("SKU-PROP")
        Fitment.objects.create(
            product=product, generation=self.gen, trim=self.tx, year_from=2012, year_to=2018,
            position="front",
        )
        Fitment.objects.create(
            product=product, generation=self.gen, engine=self.petrol,
            year_from=2009, year_to=OPEN_YEAR, is_exclusion=True,
        )
        expected = self.brute_force(product)
        indexed = set(
            FitmentIndex.objects.filter(product=product).values_list("variant_id", flat=True)
        )
        self.assertEqual(indexed, expected)
        self.assertTrue(expected)  # non-trivial case

    def test_signal_keeps_index_fresh(self):
        product = build_product("SKU-SIG")
        f = Fitment.objects.create(
            product=product, generation=self.gen, year_from=2009, year_to=OPEN_YEAR
        )
        before = FitmentIndex.objects.filter(product=product).count()
        self.assertEqual(before, 12)
        f.delete()
        self.assertEqual(FitmentIndex.objects.filter(product=product).count(), 0)

    def test_universal_not_materialised(self):
        product = build_product("SKU-UNI", is_universal=True)
        self.assertEqual(FitmentIndex.objects.filter(product=product).count(), 0)


class OfferTests(TestCase):
    def test_offer_save_does_not_crash_without_frontend(self):
        build_vehicle()
        p = build_product("SKU-OFFER")
        Offer.objects.create(product=p, price=1000)  # fires revalidate signal (thread, no-op)
