from django.db.models import Model, CharField, DateField, ForeignKey, SET_NULL, \
    TextField, DateTimeField, ManyToManyField, IntegerField, ImageField, DecimalField
from django.db.models.fields import BooleanField
from django.db.models.functions import datetime


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
    price = DecimalField(default=0)
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