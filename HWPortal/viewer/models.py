from django.db import models
from django.db.models import (
    Model,
    CharField,
    DateField,
    ForeignKey,
    SET_NULL,
    TextField,
    DateTimeField,
    ManyToManyField,
    IntegerField,
    ImageField,
    DecimalField,
    CASCADE,
)
from django.db.models.fields import BooleanField
from django.db.models.functions import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Sockets(Model):
    type = CharField(max_length=32)

    def __repr__(self):
        return self.type

    def __str__(self):
        return self.type


class BoardFormats(Model):
    format = CharField(max_length=32)

    def __repr__(self):
        return self.format

    def __str__(self):
        return self.format


class RamTypes(Model):
    type = CharField(max_length=32)

    def __repr__(self):
        return self.type

    def __str__(self):
        return self.type


class StorageTypes(Model):
    type = CharField(max_length=32)

    def __repr__(self):
        return self.type

    def __str__(self):
        return self.type


class Processors(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    socket = ForeignKey(Sockets, on_delete=SET_NULL, null=True)
    tdp = IntegerField(default=0)
    corecount = IntegerField(default=0)
    smt = BooleanField(default=False)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)
    benchresult = IntegerField(default=0)
    clock = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __repr__(self):
        return (
            f"Processor (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"socket={self.socket}, "
            f"tdp={self.tdp}, "
            f"corecount={self.corecount}, "
            f"smt={self.smt}, "
            f"price={self.price}, "
            f"benchresult={self.benchresult}), "
            f"clock={self.clock}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}"
        )

    def __str__(self):
        return self.__repr__()


class Motherboards(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    format = ForeignKey(BoardFormats, on_delete=SET_NULL, null=True)
    socket = ForeignKey(Sockets, on_delete=SET_NULL, null=True)
    maxcputdp = IntegerField(default=0)
    satacount = IntegerField(default=0)
    nvmecount = IntegerField(default=0)
    pciegen = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)

    def __repr__(self):
        return (
            f"Motherboard (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"format={self.format}, "
            f"maxcputdp={self.maxcputdp}, "
            f"satacount={self.satacount}, "
            f"nvmecount={self.nvmecount}, "
            f"pciegen={self.pciegen}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}"
        )

    def __str__(self):
        return self.__repr__()


class Ram(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    type = ForeignKey(RamTypes, on_delete=SET_NULL, null=True)
    capacity = IntegerField(default=0)
    clock = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)

    def __repr__(self):
        return (
            f"Ram (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"type={self.type}, "
            f"capacity={self.capacity}, "
            f"clock={self.clock}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}, "
        )

    def __str__(self):
        return self.__repr__()


class GraphicsCards(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    vram = IntegerField(default=0)
    tgp = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)

    def __repr__(self):
        return (
            f"Graphics card (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"vram={self.vram}, "
            f"tgp={self.tgp}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}, "
        )

    def __str__(self):
        return self.__repr__()


class Storage(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    capacity = IntegerField(default=0)
    type = ForeignKey(StorageTypes, on_delete=SET_NULL, null=True)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)

    def __repr__(self):
        return (
            f"Storage (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"capacity={self.capacity}, "
            f"type={self.type}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}, "
        )

    def __str__(self):
        return self.__repr__()


class PowerSupplyUnits(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    maxpower = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)
    price = DecimalField(default=0, decimal_places=0, max_digits=10)

    def __repr__(self):
        return (
            f"PowerSupply (name={self.name}, "
            f"manufacturer={self.manufacturer}, "
            f"maxpower={self.maxpower}, "
            f"dateadded={self.dateadded}, "
            f"rating={self.rating}, "
        )

    def __str__(self):
        return self.__repr__()


COMPONENT_TYPES = (
    ("processor", "Procesor"),
    ("motherboard", "Základní deska"),
    ("ram", "RAM"),
    ("graphics_card", "Grafická karta"),
    ("storage", "Úložiště"),
    ("power_supply", "Zdroj"),
)


class Reviews(Model):
    # Základní informace
    title = CharField(max_length=200, verbose_name="Název recenze")
    author = ForeignKey(User, on_delete=CASCADE, verbose_name="Autor")
    reviewer_name = CharField(
        max_length=100, verbose_name="Jméno recensenta", help_text="Např. TechMaster"
    )

    # Obsah recenze
    content = TextField(verbose_name="Obsah recenze")
    summary = CharField(
        max_length=500, verbose_name="Shrnutí", help_text="Krátké shrnutí recenze"
    )

    # Hodnocení
    rating = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Hodnocení",
        help_text="Hodnocení 1-5 hvězdiček",
    )

    pros = TextField(
        verbose_name="Klady", blank=True, help_text="Pozitivní stránky produktu"
    )
    cons = TextField(
        verbose_name="Zápory", blank=True, help_text="Negativní stránky produktu"
    )

    component_type = CharField(
        max_length=20, choices=COMPONENT_TYPES, verbose_name="Typ komponenty"
    )

    # Foreign keys na jednotlivé komponenty (nullable, protože recenze může být jen pro jeden typ)
    processor = ForeignKey(Processors, on_delete=CASCADE, null=True, blank=True)
    motherboard = ForeignKey(Motherboards, on_delete=CASCADE, null=True, blank=True)
    ram = ForeignKey(Ram, on_delete=CASCADE, null=True, blank=True)
    graphics_card = ForeignKey(GraphicsCards, on_delete=CASCADE, null=True, blank=True)
    storage = ForeignKey(Storage, on_delete=CASCADE, null=True, blank=True)
    power_supply = ForeignKey(
        PowerSupplyUnits, on_delete=CASCADE, null=True, blank=True
    )

    # Metadata
    date_created = DateTimeField(auto_now_add=True, verbose_name="Datum vytvoření")
    date_updated = DateTimeField(auto_now=True, verbose_name="Datum aktualizace")
    is_published = BooleanField(default=True, verbose_name="Publikováno")

    # Statistics
    helpful_votes = IntegerField(default=0, verbose_name="Užitečné hlasy")
    total_votes = IntegerField(default=0, verbose_name="Celkem hlasů")

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Recenze"
        verbose_name_plural = "Recenze"

    def __str__(self):
        return f"{self.title} - {self.reviewer_name} ({self.rating}/5)"

    def __repr__(self):
        return (
            f"Review(title={self.title}, "
            f"author={self.author}, "
            f"rating={self.rating}, "
            f"component_type={self.component_type}, "
            f"date_created={self.date_created})"
        )

    @property
    def component(self):
        """Vrátí komponentu na kterou se recenze vztahuje"""
        if self.component_type == "processor" and self.processor:
            return self.processor
        elif self.component_type == "motherboard" and self.motherboard:
            return self.motherboard
        elif self.component_type == "ram" and self.ram:
            return self.ram
        elif self.component_type == "graphics_card" and self.graphics_card:
            return self.graphics_card
        elif self.component_type == "storage" and self.storage:
            return self.storage
        elif self.component_type == "power_supply" and self.power_supply:
            return self.power_supply
        return None

    @property
    def component_name(self):
        """Vrátí název komponenty"""
        component = self.component
        return component.name if component else "Neznámá komponenta"

    @property
    def stars_display(self):
        """Vrátí hvězdičky jako string pro template"""
        return "★" * self.rating + "☆" * (5 - self.rating)

    @property
    def helpful_percentage(self):
        """Vrátí procento užitečných hlasů"""
        if self.total_votes == 0:
            return 0
        return round((self.helpful_votes / self.total_votes) * 100)


# Model pro hlasování o užitečnosti recenze
class ReviewVotes(Model):
    review = ForeignKey(Reviews, on_delete=CASCADE, related_name="votes")
    user = ForeignKey(User, on_delete=CASCADE)
    is_helpful = BooleanField(verbose_name="Užitečné")
    date_voted = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")  # Jeden uživatel může hlasovat jen jednou
        verbose_name = "Hlasování o recenzi"
        verbose_name_plural = "Hlasování o recenzích"

    def __str__(self):
        return f"{self.user.username} - {self.review.title} ({'Užitečné' if self.is_helpful else 'Neužitečné'})"


class UserFavorites(Model):
    user = ForeignKey(User, on_delete=CASCADE, verbose_name="Uživatel")
    component_type = CharField(
        max_length=20, choices=COMPONENT_TYPES, verbose_name="Typ komponenty"
    )

    # Foreign keys na jednotlivé komponenty (pouze jedna bude vyplněná)
    processor = ForeignKey(Processors, on_delete=CASCADE, null=True, blank=True)
    motherboard = ForeignKey(Motherboards, on_delete=CASCADE, null=True, blank=True)
    ram = ForeignKey(Ram, on_delete=CASCADE, null=True, blank=True)
    graphics_card = ForeignKey(GraphicsCards, on_delete=CASCADE, null=True, blank=True)
    storage = ForeignKey(Storage, on_delete=CASCADE, null=True, blank=True)
    power_supply = ForeignKey(
        PowerSupplyUnits, on_delete=CASCADE, null=True, blank=True
    )

    # Metadata
    date_added = DateTimeField(auto_now_add=True, verbose_name="Datum přidání")

    # Nastavení sledování (pro budoucí notifikace)
    watch_reviews = BooleanField(default=True, verbose_name="Sledovat nové recenze")
    watch_price_changes = BooleanField(default=True, verbose_name="Sledovat změny cen")

    class Meta:
        unique_together = [
            ("user", "processor"),
            ("user", "motherboard"),
            ("user", "ram"),
            ("user", "graphics_card"),
            ("user", "storage"),
            ("user", "power_supply"),
        ]
        ordering = ["-date_added"]
        verbose_name = "Oblíbená komponenta"
        verbose_name_plural = "Oblíbené komponenty"
        indexes = [
            # Index pro rychlé vyhledávání oblíbených podle uživatele a typu
            models.Index(fields=["user", "component_type"]),
        ]

    def __str__(self):
        component = self.component
        return f"{self.user.username} - {component.name if component else 'Neznámá komponenta'}"

    @property
    def component(self):
        """Vrátí komponentu podle typu"""
        if self.component_type == "processor" and self.processor:
            return self.processor
        elif self.component_type == "motherboard" and self.motherboard:
            return self.motherboard
        elif self.component_type == "ram" and self.ram:
            return self.ram
        elif self.component_type == "graphics_card" and self.graphics_card:
            return self.graphics_card
        elif self.component_type == "storage" and self.storage:
            return self.storage
        elif self.component_type == "power_supply" and self.power_supply:
            return self.power_supply
        return None

    @property
    def component_name(self):
        """Vrátí název komponenty"""
        component = self.component
        return component.name if component else "Neznámá komponenta"

    @property
    def component_manufacturer(self):
        """Vrátí výrobce komponenty"""
        component = self.component
        return component.manufacturer if component else "Neznámý výrobce"

    @property
    def recent_reviews_count(self):
        from datetime import datetime, timedelta

        week_ago = datetime.now() - timedelta(days=7)

        component = self.component
        if not component:
            return 0

        # Počítej recenze pro tuto komponentu za poslední týden
        filter_kwargs = {
            self.component_type: component,
            "date_created__gte": week_ago,
            "is_published": True,
        }

        return Reviews.objects.filter(**filter_kwargs).count()

    @property
    def has_recent_activity(self):
        return self.recent_reviews_count > 0


class FavoriteActivity(Model):

    ACTIVITY_TYPES = (
        ("new_review", "Nová recenze"),
        ("price_change", "Změna ceny"),
        ("rating_change", "Změna hodnocení"),
        ("new_helpful_review", "Nová užitečná recenze"),
    )

    favorite = ForeignKey(UserFavorites, on_delete=CASCADE, related_name="activities")
    activity_type = CharField(
        max_length=20, choices=ACTIVITY_TYPES, verbose_name="Typ aktivity"
    )

    # Popis aktivity
    title = CharField(max_length=200, verbose_name="Název aktivity")
    description = TextField(blank=True, verbose_name="Popis aktivity")

    # Data pro různé typy aktivit
    old_value = CharField(max_length=100, blank=True, verbose_name="Stará hodnota")
    new_value = CharField(max_length=100, blank=True, verbose_name="Nová hodnota")

    # Reference na související objekty
    related_review = ForeignKey(
        Reviews,
        on_delete=CASCADE,
        null=True,
        blank=True,
        verbose_name="Související recenze",
    )

    # Metadata
    date_created = DateTimeField(auto_now_add=True, verbose_name="Datum vytvoření")
    is_read = BooleanField(default=False, verbose_name="Přečteno")

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Aktivita oblíbené komponenty"
        verbose_name_plural = "Aktivity oblíbených komponent"

    def __str__(self):
        return f"{self.favorite.user.username} - {self.title}"

    @property
    def component_name(self):
        return self.favorite.component_name


class HeurekaClick(Model):
    component_type = CharField(max_length=20, choices=COMPONENT_TYPES)
    component_id = IntegerField()
    component_name = CharField(max_length=200)
    search_query = CharField(max_length=500)
    user = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True)
    session_key = CharField(max_length=40, blank=True)
    timestamp = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Heureka klik"
        verbose_name_plural = "Heureka kliky"
        indexes = [
            models.Index(fields=['component_type', 'component_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.component_name} - {self.timestamp.strftime('%d.%m.%Y %H:%M')}"


