from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import (BoardFormats, GraphicsCards, HeurekaClick, Motherboards,
                     PowerSupplyUnits, Processors, Ram, RamTypes, Reviews,
                     ReviewVotes, Sockets, Storage, StorageTypes,
                     UserFavorites)


class SocketsModelTest(TestCase):
    """Testy pro model Sockets"""

    def test_socket_creation(self):
        """Test vytvoření socket"""
        socket = Sockets.objects.create(type="AM4")

        self.assertEqual(socket.type, "AM4")
        self.assertEqual(str(socket), "AM4")
        self.assertEqual(repr(socket), "AM4")

    def test_socket_ordering(self):
        """Test řazení socketů"""
        socket2 = Sockets.objects.create(type="LGA1700")
        socket1 = Sockets.objects.create(type="AM4")

        sockets = list(Sockets.objects.all())
        # Měly by být seřazené podle type (AM4 před LGA1700)
        self.assertEqual(sockets[0].type, "AM4")
        self.assertEqual(sockets[1].type, "LGA1700")


class LookupTablesTest(TestCase):
    """Testy pro lookup tabulky (BoardFormats, RamTypes, StorageTypes)"""

    def test_board_formats(self):
        """Test BoardFormats model"""
        format_obj = BoardFormats.objects.create(format="ATX")

        self.assertEqual(format_obj.format, "ATX")
        self.assertEqual(str(format_obj), "ATX")

    def test_ram_types(self):
        """Test RamTypes model"""
        ram_type = RamTypes.objects.create(type="DDR4")

        self.assertEqual(ram_type.type, "DDR4")
        self.assertEqual(str(ram_type), "DDR4")

    def test_storage_types(self):
        """Test StorageTypes model"""
        storage_type = StorageTypes.objects.create(type="NVMe SSD")

        self.assertEqual(storage_type.type, "NVMe SSD")
        self.assertEqual(str(storage_type), "NVMe SSD")

    def test_lookup_tables_ordering(self):
        """Test řazení lookup tabulek"""
        # BoardFormats
        BoardFormats.objects.create(format="mITX")
        BoardFormats.objects.create(format="ATX")

        formats = list(BoardFormats.objects.all())
        self.assertEqual(formats[0].format, "ATX")  # alfabeticky první

        # RamTypes
        RamTypes.objects.create(type="DDR5")
        RamTypes.objects.create(type="DDR4")

        ram_types = list(RamTypes.objects.all())
        self.assertEqual(ram_types[0].type, "DDR4")  # alfabeticky první


class ProcessorsModelTest(TestCase):
    """Testy pro model Processors"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.socket = Sockets.objects.create(type="AM4")

    def test_processor_creation(self):
        """Test vytvoření procesoru"""
        processor = Processors.objects.create(
            name="Ryzen 5 5600X",
            manufacturer="AMD",
            socket=self.socket,
            tdp=65,
            corecount=6,
            smt=True,
            price=Decimal("8000"),
            benchresult=25000,
            clock=3700,
            rating=5,
        )

        self.assertEqual(processor.name, "Ryzen 5 5600X")
        self.assertEqual(processor.manufacturer, "AMD")
        self.assertEqual(processor.socket, self.socket)
        self.assertTrue(processor.smt)
        self.assertEqual(processor.price, Decimal("8000"))

    def test_processor_str_representation(self):
        """Test string reprezentace procesoru"""
        processor = Processors.objects.create(
            name="Test CPU", manufacturer="Test Brand", socket=self.socket, price=5000
        )

        str_repr = str(processor)
        self.assertIn("Test CPU", str_repr)
        self.assertIn("Test Brand", str_repr)

    def test_processor_defaults(self):
        """Test výchozích hodnot"""
        processor = Processors.objects.create(
            name="Basic CPU", manufacturer="Basic Brand", socket=self.socket
        )

        self.assertEqual(processor.tdp, 0)
        self.assertEqual(processor.corecount, 0)
        self.assertFalse(processor.smt)
        self.assertEqual(processor.price, Decimal("0"))
        self.assertEqual(processor.benchresult, 0)
        self.assertEqual(processor.clock, 0)
        self.assertEqual(processor.rating, 0)

    def test_processor_ordering(self):
        """Test řazení procesorů"""
        proc1 = Processors.objects.create(
            name="CPU B", manufacturer="AMD", socket=self.socket
        )
        proc2 = Processors.objects.create(
            name="CPU A", manufacturer="AMD", socket=self.socket
        )
        proc3 = Processors.objects.create(
            name="CPU C", manufacturer="Intel", socket=self.socket
        )

        processors = list(Processors.objects.all())
        # Měly by být seřazené podle manufacturer, pak name
        self.assertEqual(processors[0], proc2)  # AMD CPU A
        self.assertEqual(processors[1], proc1)  # AMD CPU B
        self.assertEqual(processors[2], proc3)  # Intel CPU C


class MotherboardsModelTest(TestCase):
    """Testy pro model Motherboards"""

    def setUp(self):
        self.socket = Sockets.objects.create(type="AM4")
        self.format = BoardFormats.objects.create(format="ATX")

    def test_motherboard_creation(self):
        """Test vytvoření základní desky"""
        mb = Motherboards.objects.create(
            name="B550 Gaming",
            manufacturer="MSI",
            format=self.format,
            socket=self.socket,
            maxcputdp=105,
            satacount=6,
            nvmecount=2,
            pciegen=4,
            rating=4,
            price=3500,
        )

        self.assertEqual(mb.name, "B550 Gaming")
        self.assertEqual(mb.manufacturer, "MSI")
        self.assertEqual(mb.socket, self.socket)
        self.assertEqual(mb.format, self.format)


class RamModelTest(TestCase):
    """Testy pro model Ram"""

    def setUp(self):
        self.ram_type = RamTypes.objects.create(type="DDR4")

    def test_ram_creation(self):
        """Test vytvoření RAM"""
        ram = Ram.objects.create(
            name="Corsair Vengeance",
            manufacturer="Corsair",
            type=self.ram_type,
            capacity=16,
            clock=3200,
            rating=5,
            price=2500,
        )

        self.assertEqual(ram.name, "Corsair Vengeance")
        self.assertEqual(ram.type, self.ram_type)
        self.assertEqual(ram.capacity, 16)


class StorageModelTest(TestCase):
    """Testy pro model Storage"""

    def setUp(self):
        self.storage_type = StorageTypes.objects.create(type="NVMe SSD")

    def test_storage_creation(self):
        """Test vytvoření úložiště"""
        storage = Storage.objects.create(
            name="Samsung 980 Pro",
            manufacturer="Samsung",
            capacity=1000,
            type=self.storage_type,
            rating=5,
            price=4000,
        )

        self.assertEqual(storage.name, "Samsung 980 Pro")
        self.assertEqual(storage.type, self.storage_type)
        self.assertEqual(storage.capacity, 1000)


class PowerSupplyUnitsModelTest(TestCase):
    """Testy pro model PowerSupplyUnits"""

    def test_psu_creation(self):
        """Test vytvoření zdroje"""
        psu = PowerSupplyUnits.objects.create(
            name="Seasonic Focus GX-750",
            manufacturer="Seasonic",
            maxpower=750,
            rating=5,
            price=3500,
        )

        self.assertEqual(psu.name, "Seasonic Focus GX-750")
        self.assertEqual(psu.manufacturer, "Seasonic")
        self.assertEqual(psu.maxpower, 750)


class ReviewsModelTest(TestCase):
    """Testy pro model Reviews"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.socket = Sockets.objects.create(type="AM4")
        self.processor = Processors.objects.create(
            name="Test CPU", manufacturer="Test Brand", socket=self.socket, price=5000
        )

    def test_review_creation(self):
        """Test vytvoření recenze"""
        review = Reviews.objects.create(
            title="Skvělý procesor",
            author=self.user,
            reviewer_name="TechReviewer",
            content="Výborný výkon za dobrou cenu.",
            summary="Doporučuji!",
            rating=5,
            component_type="processor",
            processor=self.processor,
            pros="Rychlý\nTichý",
            cons="Trochu drahý",
        )

        self.assertEqual(review.title, "Skvělý procesor")
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.component_type, "processor")
        self.assertEqual(review.processor, self.processor)

    def test_review_str_representation(self):
        """Test string reprezentace recenze"""
        review = Reviews.objects.create(
            title="Test Review",
            author=self.user,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=4,
            component_type="processor",
            processor=self.processor,
        )

        str_repr = str(review)
        expected = "Test Review - TestReviewer (4/5)"
        self.assertEqual(str_repr, expected)

    def test_review_component_property(self):
        """Test component property"""
        review = Reviews.objects.create(
            title="Test Review",
            author=self.user,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=4,
            component_type="processor",
            processor=self.processor,
        )

        # Test component property
        self.assertEqual(review.component, self.processor)

        # Test component_name property
        self.assertEqual(review.component_name, "Test CPU")

    def test_review_stars_display_property(self):
        """Test stars_display property"""
        review = Reviews.objects.create(
            title="Test Review",
            author=self.user,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=3,
            component_type="processor",
            processor=self.processor,
        )

        stars = review.stars_display
        self.assertEqual(stars, "★★★☆☆")

    def test_review_helpful_percentage_property(self):
        """Test helpful_percentage property"""
        review = Reviews.objects.create(
            title="Test Review",
            author=self.user,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=4,
            component_type="processor",
            processor=self.processor,
            helpful_votes=8,
            total_votes=10,
        )

        percentage = review.helpful_percentage
        self.assertEqual(percentage, 80)

        # Test s nulovými hlasy
        review.total_votes = 0
        self.assertEqual(review.helpful_percentage, 0)

    def test_review_rating_validation(self):
        """Test validace hodnocení (1-5)"""
        # Validní hodnocení
        review = Reviews.objects.create(
            title="Test Review",
            author=self.user,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=5,
            component_type="processor",
            processor=self.processor,
        )

        review.full_clean()  # Nemělo by vyhodit chybu

        # Nevalidní hodnocení
        review.rating = 6
        with self.assertRaises(ValidationError):
            review.full_clean()

        review.rating = 0
        with self.assertRaises(ValidationError):
            review.full_clean()


class ReviewVotesModelTest(TestCase):
    """Testy pro model ReviewVotes"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )
        self.socket = Sockets.objects.create(type="AM4")
        self.processor = Processors.objects.create(
            name="Test CPU", manufacturer="Test", socket=self.socket, price=5000
        )
        self.review = Reviews.objects.create(
            title="Test Review",
            author=self.user1,
            reviewer_name="TestReviewer",
            content="Test content",
            summary="Test summary",
            rating=4,
            component_type="processor",
            processor=self.processor,
        )

    def test_review_vote_creation(self):
        """Test vytvoření hlasování"""
        vote = ReviewVotes.objects.create(
            review=self.review, user=self.user2, is_helpful=True
        )

        self.assertEqual(vote.review, self.review)
        self.assertEqual(vote.user, self.user2)
        self.assertTrue(vote.is_helpful)

    def test_review_vote_unique_constraint(self):
        """Test unique constraint - jeden uživatel může hlasovat jen jednou"""
        # První hlasování OK
        ReviewVotes.objects.create(review=self.review, user=self.user2, is_helpful=True)

        # Druhé hlasování by mělo selhat
        with self.assertRaises(IntegrityError):
            ReviewVotes.objects.create(
                review=self.review, user=self.user2, is_helpful=False
            )


class UserFavoritesModelTest(TestCase):
    """Testy pro model UserFavorites"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.socket = Sockets.objects.create(type="AM4")
        self.processor = Processors.objects.create(
            name="Test CPU", manufacturer="Test", socket=self.socket, price=5000
        )

    def test_user_favorite_creation(self):
        """Test vytvoření oblíbené komponenty"""
        favorite = UserFavorites.objects.create(
            user=self.user,
            component_type="processor",
            processor=self.processor,
            watch_reviews=True,
            watch_price_changes=False,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.component_type, "processor")
        self.assertEqual(favorite.processor, self.processor)
        self.assertTrue(favorite.watch_reviews)
        self.assertFalse(favorite.watch_price_changes)

    def test_user_favorite_component_property(self):
        """Test component property"""
        favorite = UserFavorites.objects.create(
            user=self.user, component_type="processor", processor=self.processor
        )

        # Test component property
        self.assertEqual(favorite.component, self.processor)

        # Test component_name property
        self.assertEqual(favorite.component_name, "Test CPU")

        # Test component_manufacturer property
        self.assertEqual(favorite.component_manufacturer, "Test")


class HeurekaClickModelTest(TestCase):
    """Testy pro model HeurekaClick"""

    def setUp(self):
        """Příprava testovacích dat"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_heureka_click_creation(self):
        """Test vytvoření Heureka kliku"""
        click = HeurekaClick.objects.create(
            component_type="processor",
            component_id=123,
            component_name="AMD Ryzen 5 5600X",
            search_query="AMD Ryzen 5 5600X cena",
            user=self.user,
            session_key="test_session_123",
        )

        self.assertEqual(click.component_type, "processor")
        self.assertEqual(click.component_id, 123)
        self.assertEqual(click.component_name, "AMD Ryzen 5 5600X")
        self.assertEqual(click.user, self.user)

    def test_heureka_click_str_representation(self):
        """Test string reprezentace"""
        click = HeurekaClick.objects.create(
            component_type="processor",
            component_id=123,
            component_name="Test Component",
            search_query="test query",
            user=self.user,
        )

        str_repr = str(click)
        self.assertIn("Test Component", str_repr)


# Pomocné testy pro coverage
class ModelsIntegrationTest(TestCase):
    """Integrační testy mezi modely"""

    def setUp(self):
        """Příprava komplexnějších testovacích dat"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.socket = Sockets.objects.create(type="AM4")
        self.processor = Processors.objects.create(
            name="Test CPU", manufacturer="AMD", socket=self.socket, price=5000
        )

    def test_processor_with_reviews_and_favorites(self):
        """Test procesoru s recenzemi a oblíbenými"""
        # Vytvoř recenzi
        review = Reviews.objects.create(
            title="Great CPU",
            author=self.user,
            reviewer_name="TestUser",
            content="Excellent performance",
            summary="Recommended",
            rating=5,
            component_type="processor",
            processor=self.processor,
        )

        # Vytvoř oblíbenou
        favorite = UserFavorites.objects.create(
            user=self.user, component_type="processor", processor=self.processor
        )

        # Ověř propojení
        self.assertEqual(review.component, self.processor)
        self.assertEqual(favorite.component, self.processor)
        self.assertEqual(review.component_name, favorite.component_name)

    def test_model_meta_options(self):
        """Test Meta options modelů"""
        # Test verbose names
        self.assertEqual(Sockets._meta.verbose_name, "Socket")
        self.assertEqual(Sockets._meta.verbose_name_plural, "Sockety")

        # Test ordering - vyčistíme databázi před testem
        Sockets.objects.all().delete()  # Vymaž všechny existující sockety z předchozích testů

        socket1 = Sockets.objects.create(type="Z")
        socket2 = Sockets.objects.create(type="A")

        sockets = list(Sockets.objects.all())
        self.assertEqual(sockets[0].type, "A")  # Mělo by být první
        self.assertEqual(sockets[1].type, "Z")  # Mělo by být druhé
