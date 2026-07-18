from django.db import models
from django.db.models import F, Q

# Sentinel for "still in production" — NEVER use NULL for year_to.
# NULL forces OR-clauses that MySQL will not index; 9999 keeps the
# overlap test a pure BETWEEN-style index seek.
OPEN_YEAR = 9999

FUEL = [
    ("petrol", "Petrol"),
    ("diesel", "Diesel"),
    ("hybrid", "Hybrid"),
    ("electric", "Electric"),
    ("lpg", "LPG"),
]


class VehicleMake(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="makes/", blank=True)
    popularity = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-popularity", "name"]

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT, related_name="models")
    name = models.CharField(max_length=120)
    slug = models.SlugField()

    class Meta:
        unique_together = [("make", "slug")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.make.name} {self.name}"


class VehicleModelAlias(models.Model):
    """No ArrayField on MySQL. Aliases power search + old-URL redirects."""

    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=120, db_index=True)

    class Meta:
        verbose_name_plural = "vehicle model aliases"

    def __str__(self):
        return self.alias


class VehicleGeneration(models.Model):
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT, related_name="generations")
    code = models.CharField(max_length=40)
    slug = models.SlugField()
    year_from = models.PositiveSmallIntegerField()
    year_to = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    body_type = models.CharField(max_length=40, blank=True)
    facelift = models.CharField(max_length=40, blank=True)
    image = models.ImageField(upload_to="generations/", blank=True)

    class Meta:
        unique_together = [("model", "slug")]
        ordering = ["-year_from"]

    def __str__(self):
        return f"{self.model} {self.code}"

    @property
    def year_display(self):
        end = "present" if self.year_to == OPEN_YEAR else self.year_to
        return f"{self.year_from}–{end}"


class VehicleTrim(models.Model):
    generation = models.ForeignKey(VehicleGeneration, on_delete=models.PROTECT, related_name="trims")
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    class Meta:
        unique_together = [("generation", "slug")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.generation} {self.name}"


class VehicleEngine(models.Model):
    generation = models.ForeignKey(VehicleGeneration, on_delete=models.PROTECT, related_name="engines")
    display = models.CharField(max_length=80)
    code = models.CharField(max_length=40, blank=True)
    slug = models.SlugField()
    fuel = models.CharField(max_length=16, choices=FUEL)
    capacity_cc = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("generation", "slug")]

    def __str__(self):
        label = f"{self.display} · {self.code}" if self.code else self.display
        return f"{self.generation} {label}"


class VehicleVariant(models.Model):
    """The atomic vehicle. A part fits (or does not fit) THIS."""

    generation = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE, related_name="variants")
    trim = models.ForeignKey(VehicleTrim, null=True, blank=True, on_delete=models.CASCADE)
    engine = models.ForeignKey(VehicleEngine, null=True, blank=True, on_delete=models.CASCADE)
    drivetrain = models.CharField(max_length=8, blank=True)  # "" = any
    transmission = models.CharField(max_length=16, blank=True)
    year_from = models.PositiveSmallIntegerField()
    year_to = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    market = models.CharField(max_length=8, default="KE")  # KE / JP-import / EU
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["generation", "year_from", "year_to"])]
        constraints = [
            models.CheckConstraint(check=Q(year_to__gte=F("year_from")), name="variant_year_order")
        ]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        gen = self.generation
        bits = [gen.model.make.name, gen.model.name, gen.code]
        if self.trim_id:
            bits.append(self.trim.name)
        if self.engine_id:
            bits.append(self.engine.display)
        end = "present" if self.year_to == OPEN_YEAR else self.year_to
        bits.append(f"{self.year_from}-{end}")
        return " ".join(str(b) for b in bits)


class VariantGroup(models.Model):
    """
    A set of VehicleVariants sharing an IDENTICAL resolved product set.
    ONE SEO page per group — the anti-thin-content weapon.
    """

    generation = models.ForeignKey(VehicleGeneration, on_delete=models.CASCADE, related_name="groups")
    trim = models.ForeignKey(VehicleTrim, null=True, blank=True, on_delete=models.CASCADE)
    engine = models.ForeignKey(VehicleEngine, null=True, blank=True, on_delete=models.CASCADE)
    year_from = models.PositiveSmallIntegerField()
    year_to = models.PositiveSmallIntegerField(default=OPEN_YEAR)
    slug_years = models.CharField(max_length=16)  # "2018-2023"
    fingerprint = models.CharField(max_length=64, db_index=True)  # sha256 of sorted product ids
    canonical_path = models.CharField(max_length=400, unique=True)
    product_count = models.PositiveIntegerField(default=0)
    variants = models.ManyToManyField(VehicleVariant, related_name="groups")

    def __str__(self):
        return self.canonical_path


class VehicleRegistrationLookup(models.Model):
    """Kenyans search by KDA 123A, not by trim. Cache every resolution forever."""

    plate = models.CharField(max_length=16, db_index=True)
    vin = models.CharField(max_length=32, blank=True, db_index=True)
    variant = models.ForeignKey(VehicleVariant, null=True, blank=True, on_delete=models.SET_NULL)
    raw_payload = models.JSONField(default=dict, blank=True)
    confidence = models.FloatField(default=0)
    resolved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plate
