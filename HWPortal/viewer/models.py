from django.db.models import Model, CharField, DateField, ForeignKey, SET_NULL, \
    TextField, DateTimeField, ManyToManyField, IntegerField, ImageField, DecimalField
from django.db.models.fields import BooleanField
from django.db.models.functions import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Sockets(Model):
    type = CharField(max_length=32)

class BoardFormats(Model):
    format = CharField(max_length=32)

class RamTypes(Model):
    type = CharField(max_length=32)

class Processors(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    socket = ForeignKey(Sockets, on_delete=SET_NULL, null=True)
    tdp = IntegerField(default=0)
    corecount = IntegerField(default=0)
    smt = BooleanField(default=False)
    price = DecimalField(default=0, decimal_places=2, max_digits=10)
    benchresult = IntegerField(default=0)
    clock = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __repr__(self):
        return (f"Processor (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"socket={self.socket}, "
                f"tdp={self.tdp}, "
                f"corecount={self.corecount}, "
                f"smt={self.smt}, "
                f"price={self.price}, "
                f"benchresult={self.benchresult}), "
                f"clock={self.clock}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}")

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

    def __repr__(self):
        return (f"Motherboard (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"format={self.format}, "
                f"maxcputdp={self.maxcputdp}, "
                f"satacount={self.satacount}, "
                f"nvmecount={self.nvmecount}, "
                f"pciegen={self.pciegen}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}")

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

    def __repr__(self):
        return (f"Ram (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"type={self.type}, "
                f"capacity={self.capacity}, "
                f"clock={self.clock}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}, ")

    def __str__(self):
        return self.__repr__()

class GraphicsCards(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    vram = IntegerField(default=0)
    tgp = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)

    def __repr__(self):
        return (f"Graphics card (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"vram={self.vram}, "
                f"tgp={self.tgp}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}, ")

    def __str__(self):
        return self.__repr__()

STORAGE_TYPES = (
    (1, 'sata'),
    (2, 'nvme')
)

class Storage(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    capacity = IntegerField(default=0)
    type = CharField(choices=STORAGE_TYPES)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)

    def __repr__(self):
        return (f"Storage (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"capacity={self.capacity}, "
                f"type={self.type}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}, ")

    def __str__(self):
        return self.__repr__()

class PowerSupplyUnits(Model):
    name = CharField(max_length=100)
    manufacturer = CharField(max_length=100)
    maxpower = IntegerField(default=0)
    dateadded = DateField(auto_now=True)
    rating = IntegerField(default=0)

    def __repr__(self):
        return (f"PowerSupply (name={self.name}, "
                f"manufacturer={self.manufacturer}, "
                f"maxpower={self.maxpower}, "
                f"dateadded={self.dateadded}, "
                f"rating={self.rating}, ")

    def __str__(self):
        return self.__repr__()

COMPONENT_TYPES = (
    ('processor', 'Procesor'),
    ('motherboard', 'Základní deska'),
    ('ram', 'RAM'),
    ('graphics_card', 'Grafická karta'),
    ('storage', 'Úložiště'),
    ('power_supply', 'Zdroj'),
)


class Reviews(Model):
    # Základní informace
    title = CharField(max_length=200, verbose_name="Název recenze")
    author = ForeignKey(User, on_delete=CASCADE, verbose_name="Autor")
    reviewer_name = CharField(max_length=100, verbose_name="Jméno recensenta", help_text="Např. TechMaster")

    # Obsah recenze
    content = TextField(verbose_name="Obsah recenze")
    summary = CharField(max_length=500, verbose_name="Shrnutí", help_text="Krátké shrnutí recenze")

    # Hodnocení
    rating = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Hodnocení",
        help_text="Hodnocení 1-5 hvězdiček"
    )

    pros = TextField(verbose_name="Klady", blank=True, help_text="Pozitivní stránky produktu")
    cons = TextField(verbose_name="Zápory", blank=True, help_text="Negativní stránky produktu")

    component_type = CharField(max_length=20, choices=COMPONENT_TYPES, verbose_name="Typ komponenty")

    # Foreign keys na jednotlivé komponenty (nullable, protože recenze může být jen pro jeden typ)
    processor = ForeignKey(Processors, on_delete=CASCADE, null=True, blank=True)
    motherboard = ForeignKey(Motherboards, on_delete=CASCADE, null=True, blank=True)
    ram = ForeignKey(Ram, on_delete=CASCADE, null=True, blank=True)
    graphics_card = ForeignKey(GraphicsCards, on_delete=CASCADE, null=True, blank=True)
    storage = ForeignKey(Storage, on_delete=CASCADE, null=True, blank=True)
    power_supply = ForeignKey(PowerSupplyUnits, on_delete=CASCADE, null=True, blank=True)

    # Metadata
    date_created = DateTimeField(auto_now_add=True, verbose_name="Datum vytvoření")
    date_updated = DateTimeField(auto_now=True, verbose_name="Datum aktualizace")
    is_published = BooleanField(default=True, verbose_name="Publikováno")

    # Statistics
    helpful_votes = IntegerField(default=0, verbose_name="Užitečné hlasy")
    total_votes = IntegerField(default=0, verbose_name="Celkem hlasů")

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Recenze"
        verbose_name_plural = "Recenze"

    def __str__(self):
        return f"{self.title} - {self.reviewer_name} ({self.rating}/5)"

    def __repr__(self):
        return (f"Review(title={self.title}, "
                f"author={self.author}, "
                f"rating={self.rating}, "
                f"component_type={self.component_type}, "
                f"date_created={self.date_created})")

    @property
    def component(self):
        """Vrátí komponentu na kterou se recenze vztahuje"""
        if self.component_type == 'processor' and self.processor:
            return self.processor
        elif self.component_type == 'motherboard' and self.motherboard:
            return self.motherboard
        elif self.component_type == 'ram' and self.ram:
            return self.ram
        elif self.component_type == 'graphics_card' and self.graphics_card:
            return self.graphics_card
        elif self.component_type == 'storage' and self.storage:
            return self.storage
        elif self.component_type == 'power_supply' and self.power_supply:
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
    review = ForeignKey(Reviews, on_delete=CASCADE, related_name='votes')
    user = ForeignKey(User, on_delete=CASCADE)
    is_helpful = BooleanField(verbose_name="Užitečné")
    date_voted = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')  # Jeden uživatel může hlasovat jen jednou
        verbose_name = "Hlasování o recenzi"
        verbose_name_plural = "Hlasování o recenzích"

    def __str__(self):
        return f"{self.user.username} - {self.review.title} ({'Užitečné' if self.is_helpful else 'Neužitečné'})"