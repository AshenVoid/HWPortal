from django.test import TestCase

# Create your tests here.
"""
Centrální test suite pro HWPortal aplikaci
Spouští všechne typy testů podle zadání: models, forms, GUI

Použití:
    python manage.py test viewer --settings=HWPortal.test_settings
    python manage.py test viewer.tests --settings=HWPortal.test_settings
"""

import unittest
from django.test import TestCase, tag
from django.test.utils import override_settings

# ================================
# IMPORT VŠECH TESTŮ
# ================================

# Models testy
from .test_models import (
    SocketsModelTest,
    LookupTablesTest,
    ProcessorsModelTest,
    ReviewsModelTest,
    ReviewVotesModelTest,
    UserFavoritesModelTest,
    HeurekaClickModelTest,
    ModelsIntegrationTest
)

# Selenium testy
from .test_selenium import (
    FormsSeleniumTests,
    QuickFormsTests
)


# ================================
# TEST SUITE CLASSES
# ================================

class AllTestsSuite(TestCase):
    """
    Test suite který organizuje všechny testy podle kategorií
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 60)
        print("🚀 SPOUŠTÍM KOMPLETNÍ TEST SUITE")
        print("=" * 60)
        print("📊 Pokrytí: Models, Forms, GUI (Selenium)")
        print("⚡ Optimalizováno pro rychlost a spolehlivost")
        print("=" * 60 + "\n")


@tag('models')
class ModelsTestSuite(TestCase):
    """Test suite pouze pro models"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n🔬 Models Test Suite - Unit testy")


@tag('forms', 'selenium')
class FormsTestSuite(TestCase):
    """Test suite pouze pro forms a GUI"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n📝 Forms & GUI Test Suite - Selenium testy")


@tag('quick')
class QuickTestSuite(TestCase):
    """Rychlé testy pro základní ověření"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n⚡ Quick Test Suite - Základní ověření")


# ================================
# POMOCNÉ FUNKCE PRO SPOUŠTĚNÍ
# ================================

def run_models_tests():
    """Spustí pouze models testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Přidej všechny models test třídy
    models_tests = [
        SocketsModelTest,
        LookupTablesTest,
        ProcessorsModelTest,
        ReviewsModelTest,
        ReviewVotesModelTest,
        UserFavoritesModelTest,
        HeurekaClickModelTest,
        ModelsIntegrationTest
    ]

    for test_class in models_tests:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


def run_selenium_tests():
    """Spustí pouze Selenium testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Přidej Selenium test třídy
    selenium_tests = [
        FormsSeleniumTests,
        QuickFormsTests
    ]

    for test_class in selenium_tests:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


def run_all_tests():
    """Spustí všechny testy v optimálním pořadí"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    print("🔄 Připravuji test suite...")

    # Nejdřív rychlé models testy
    models_suite = run_models_tests()
    suite.addTest(models_suite)

    # Pak Selenium testy
    selenium_suite = run_selenium_tests()
    suite.addTest(selenium_suite)

    return suite


# ================================
# CUSTOM TEST COMMANDS
# ================================

class TestCommand:
    """
    Pomocná třída pro různé způsoby spouštění testů
    """

    @staticmethod
    def models_only():
        """
        Spustí pouze models testy
        Použití: python manage.py test viewer.tests.TestCommand.models_only
        """
        return run_models_tests()

    @staticmethod
    def selenium_only():
        """
        Spustí pouze Selenium testy
        Použití: python manage.py test viewer.tests.TestCommand.selenium_only
        """
        return run_selenium_tests()

    @staticmethod
    def full_suite():
        """
        Spustí všechny testy
        Použití: python manage.py test viewer.tests.TestCommand.full_suite
        """
        return run_all_tests()


# ================================
# DEMO TESTY PRO OVĚŘENÍ
# ================================

class TestSuiteDemo(TestCase):
    """Demo testy pro ověření že test runner funguje"""

    def test_models_import(self):
        """Test že se models testy správně importují"""
        from .test_models import ProcessorsModelTest
        self.assertTrue(hasattr(ProcessorsModelTest, 'test_processor_creation'))
        print("✓ Models testy importovány správně")

    def test_selenium_import(self):
        """Test že se Selenium testy správně importují"""
        from .test_selenium import FormsSeleniumTests
        self.assertTrue(hasattr(FormsSeleniumTests, 'test_login_form_structure_and_styling'))
        print("✓ Selenium testy importovány správně")

    def test_suite_structure(self):
        """Test struktury test suite"""
        models_suite = run_models_tests()
        selenium_suite = run_selenium_tests()

        self.assertGreater(models_suite.countTestCases(), 0)
        self.assertGreater(selenium_suite.countTestCases(), 0)
        print(f"✓ Models suite: {models_suite.countTestCases()} testů")
        print(f"✓ Selenium suite: {selenium_suite.countTestCases()} testů")


# ================================
# SUMMARY INFO
# ================================

def get_test_summary():
    """Vrátí přehled všech dostupných testů"""
    return {
        'total_models_tests': 28,
        'total_selenium_tests': 21,
        'total_tests': 49,
        'categories': ['Models', 'Forms', 'GUI'],
        'frameworks': ['Django TestCase', 'Selenium WebDriver'],
        'coverage': ['Unit Tests', 'Integration Tests', 'E2E Tests']
    }


if __name__ == '__main__':
    """Spuštění při přímém volání souboru"""
    print("🧪 HWPortal Test Suite")
    print("=" * 40)
    summary = get_test_summary()
    print(f"📊 Celkem testů: {summary['total_tests']}")
    print(f"🔬 Models: {summary['total_models_tests']} testů")
    print(f"📝 Selenium: {summary['total_selenium_tests']} testů")
    print(f"🎯 Kategorie: {', '.join(summary['categories'])}")
    print("=" * 40)
    print("\n📋 Příkazy pro spouštění:")
    print("• Všechny testy: python manage.py test viewer --settings=HWPortal.test_settings")
    print("• Jen models: python manage.py test viewer.test_models --settings=HWPortal.test_settings")
    print("• Jen selenium: python manage.py test viewer.test_selenium --settings=HWPortal.test_settings")
    print("• Rychlé testy: python manage.py test viewer.test_selenium.QuickFormsTests --settings=HWPortal.test_settings")

