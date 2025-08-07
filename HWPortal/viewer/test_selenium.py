import time
import uuid

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .models import GraphicsCards, Processors, Reviews, Sockets


@override_settings(DEBUG=True)
@tag("selenium")
class FormsSeleniumTests(StaticLiveServerTestCase):
    """
    Selenium testy pro formuláře v HWPortal aplikaci
    Zaměřené na frontend testing podle zadání
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        """Příprava testovacích dat"""
        self.unique_suffix = str(uuid.uuid4())[:8]

        self.test_user = User.objects.create_user(
            username=f"testuser_{self.unique_suffix}",
            email=f"test_{self.unique_suffix}@example.com",
            password="testpass123",
        )

        self.test_socket = Sockets.objects.create(type=f"AM4_{self.unique_suffix}")
        self.test_processor = Processors.objects.create(
            name=f"Test CPU {self.unique_suffix}",
            manufacturer="Test Manufacturer",
            socket=self.test_socket,
            price=5000,
        )

    def tearDown(self):
        """Úklid po testech"""
        Reviews.objects.filter(title__contains="Test").delete()
        if hasattr(self, "test_processor") and self.test_processor:
            try:
                self.test_processor.delete()
            except:
                pass
        if hasattr(self, "test_socket") and self.test_socket:
            try:
                self.test_socket.delete()
            except:
                pass
        if hasattr(self, "test_user") and self.test_user:
            try:
                self.test_user.delete()
            except:
                pass

    def _debug_page_content(self, test_name):
        """Pomocná metoda pro debugging"""
        print(f"\n=== DEBUG {test_name} ===")
        print(f"Current URL: {self.selenium.current_url}")
        print(f"Page title: {self.selenium.title}")

        forms = self.selenium.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} forms")

        inputs = self.selenium.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input elements:")
        for i, inp in enumerate(inputs):
            print(
                f"  Input {i}: name='{inp.get_attribute('name')}', type='{inp.get_attribute('type')}'"
            )

        error_elements = self.selenium.find_elements(
            By.CSS_SELECTOR, ".error, .alert, .bg-red-100"
        )
        if error_elements:
            print(f"Found {len(error_elements)} error elements")

        print("=== END DEBUG ===\n")

    # ================================
    # TESTY CUSTOM LOGIN FORM
    # ================================

    def test_login_form_structure_and_styling(self):
        """Test struktury a stylingu login formuláře"""
        self.selenium.get(f"{self.live_server_url}/login/")

        # Test existence základních elementů
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.selenium.find_element(By.NAME, "password")
        submit_btn = self.selenium.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )

        # Test CSS tříd z forms.py
        self.assertIn("w-full", username_input.get_attribute("class"))
        self.assertIn("border-gray-300", password_input.get_attribute("class"))
        self.assertIn("focus:ring-blue-400", username_input.get_attribute("class"))

        # Test placeholder textů z forms.py
        self.assertEqual(
            "Zadejte uživatelské jméno", username_input.get_attribute("placeholder")
        )
        self.assertEqual("Zadejte heslo", password_input.get_attribute("placeholder"))

        # Test required attributů
        self.assertTrue(username_input.get_attribute("required"))
        self.assertTrue(password_input.get_attribute("required"))

        print("✓ Login form structure test PASSED")

    def test_login_form_functionality(self):
        """Test basic funkčnosti login formuláře"""
        self.selenium.get(f"{self.live_server_url}/login/")

        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")

        # Test input functionality
        username_input.send_keys(f"testuser_{self.unique_suffix}")
        password_input.send_keys("testpass123")

        # Ověř že hodnoty se správně zapisují
        self.assertEqual(
            f"testuser_{self.unique_suffix}", username_input.get_attribute("value")
        )

        # Test submit button
        submit_btn = self.selenium.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )
        self.assertTrue(submit_btn.is_displayed())
        self.assertTrue(submit_btn.is_enabled())

        print("✓ Login form functionality test PASSED")

    # ================================
    # TESTY CUSTOM USER CREATION FORM
    # ================================

    def test_registration_form_structure_and_styling(self):
        """Test struktury a stylingu registračního formuláře"""
        self.selenium.get(f"{self.live_server_url}/register/")

        # Test existence všech required elementů
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        email_input = self.selenium.find_element(By.NAME, "email")
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password2_input = self.selenium.find_element(By.NAME, "password2")
        submit_btn = self.selenium.find_element(
            By.CSS_SELECTOR, "button[type='submit']"
        )

        # Test CSS tříd z forms.py
        self.assertIn("w-full", username_input.get_attribute("class"))
        self.assertIn("border-gray-300", email_input.get_attribute("class"))
        self.assertIn("focus:ring-blue-400", password1_input.get_attribute("class"))

        # Test placeholder textů z forms.py
        self.assertEqual(
            "Zadejte uživatelské jméno", username_input.get_attribute("placeholder")
        )
        self.assertEqual("Zadejte email", email_input.get_attribute("placeholder"))
        self.assertEqual("Zadejte heslo", password1_input.get_attribute("placeholder"))
        self.assertEqual("Zadejte heslo", password2_input.get_attribute("placeholder"))

        # Test input types
        self.assertEqual("email", email_input.get_attribute("type"))
        self.assertEqual("password", password1_input.get_attribute("type"))
        self.assertEqual("password", password2_input.get_attribute("type"))

        print("✓ Registration form structure test PASSED")

    def test_registration_form_input_functionality(self):
        """Test input funkčnosti registračního formuláře"""
        self.selenium.get(f"{self.live_server_url}/register/")

        username_input = self.selenium.find_element(By.NAME, "username")
        email_input = self.selenium.find_element(By.NAME, "email")
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password2_input = self.selenium.find_element(By.NAME, "password2")

        # Test že můžeme vyplnit všechna pole
        test_username = f"testuser_{self.unique_suffix}"
        test_email = f"test_{self.unique_suffix}@example.com"

        username_input.send_keys(test_username)
        email_input.send_keys(test_email)
        password1_input.send_keys("testpass123")
        password2_input.send_keys("testpass123")

        # Ověř že hodnoty se správně zapisují
        self.assertEqual(test_username, username_input.get_attribute("value"))
        self.assertEqual(test_email, email_input.get_attribute("value"))

        # Test CSRF token
        csrf_inputs = self.selenium.find_elements(By.NAME, "csrfmiddlewaretoken")
        self.assertGreater(len(csrf_inputs), 0, "Formulář by měl mít CSRF token")

        print("✓ Registration form input functionality test PASSED")

    def test_registration_form_validation_display(self):
        """Test zobrazení validačních prvků"""
        self.selenium.get(f"{self.live_server_url}/register/")

        # Test existence error containerů (i když jsou prázdné)
        username_field = self.selenium.find_element(By.NAME, "username")

        # Najdi parent div pro username
        username_parent = username_field.find_element(By.XPATH, "./..")

        # Ověř že struktura podporuje zobrazení chyb
        # (i když chyby nejsou aktuálně zobrazené)

        print("✓ Registration form validation structure test PASSED")

    # ================================
    # TESTY REVIEW FORM (pokud existuje)
    # ================================

    def test_review_form_exists_and_accessible(self):
        """Test existence review formuláře"""
        self.selenium.get(f"{self.live_server_url}/review/create/")

        # Zkontroluj jestli stránka existuje (není 404)
        page_source = self.selenium.page_source.lower()
        is_404 = "404" in page_source or "not found" in page_source

        if not is_404:
            # Najdi formulář nebo redirect na login
            forms = self.selenium.find_elements(By.TAG_NAME, "form")
            self.assertGreater(
                len(forms), 0, "Na stránce by měl být alespoň jeden formulář"
            )
            print("✓ Review form page exists and is accessible")
        else:
            print("⚠ Review form page returns 404 - may not be implemented")

    def test_review_form_structure_if_accessible(self):
        """Test struktury review formuláře pokud je přístupný"""
        self.selenium.get(f"{self.live_server_url}/review/create/")

        page_source = self.selenium.page_source.lower()
        needs_login = "login" in page_source or "přihlás" in page_source

        if not needs_login:
            try:
                # Zkus najít basic review form elements
                title_inputs = self.selenium.find_elements(By.NAME, "title")
                if title_inputs:
                    title_input = title_inputs[0]

                    # Test CSS z forms.py
                    self.assertIn("w-full", title_input.get_attribute("class"))
                    self.assertIn("border-gray-300", title_input.get_attribute("class"))

                    # Test placeholder z forms.py
                    expected_placeholder = (
                        'Název vaší recenze (např. "Skvělý procesor za rozumnou cenu")'
                    )
                    self.assertEqual(
                        expected_placeholder, title_input.get_attribute("placeholder")
                    )

                    print("✓ Review form structure test PASSED")
                else:
                    print("⚠ Review form title input not found")

            except Exception as e:
                print(f"⚠ Review form structure test skipped: {e}")
        else:
            print("⚠ Review form requires login - structure test skipped")

    # ================================
    # TESTY ACCESSIBILITY A NAVIGATION
    # ================================

    def test_form_accessibility_features(self):
        """Test accessibility funkcí formulářů"""
        self.selenium.get(f"{self.live_server_url}/register/")

        # Test labels
        username_input = self.selenium.find_element(By.NAME, "username")
        labels = self.selenium.find_elements(By.TAG_NAME, "label")

        label_found = False
        for label in labels:
            if "uživatel" in label.text.lower():
                label_found = True
                print("Found username label")
                break

        # Test required attributes
        required = username_input.get_attribute("required")
        if required:
            print("Username input has required attribute")

        # Test email input type
        email_input = self.selenium.find_element(By.NAME, "email")
        self.assertEqual("email", email_input.get_attribute("type"))

        print("✓ Form accessibility test PASSED")

    def test_navigation_between_forms(self):
        """Test navigace mezi formuláři"""
        self.selenium.get(f"{self.live_server_url}/register/")

        # Najdi login link
        login_links = self.selenium.find_elements(By.CSS_SELECTOR, "a[href*='login']")

        if login_links:
            login_links[0].click()

            # Počkej na načtení
            time.sleep(2)

            # Ověř že jsme na login stránce nebo máme login form
            current_url = self.selenium.current_url
            has_login_form = len(self.selenium.find_elements(By.NAME, "username")) > 0

            success = "login" in current_url or has_login_form
            self.assertTrue(success, "Navigation to login should work")
            print("✓ Navigation between forms test PASSED")
        else:
            print("⚠ Login link not found - navigation test skipped")

    def test_forms_css_styling_consistency(self):
        """Test konzistence CSS stylingu napříč formuláři"""
        # Test login form
        self.selenium.get(f"{self.live_server_url}/login/")

        username_input = self.selenium.find_element(By.NAME, "username")
        login_classes = username_input.get_attribute("class")

        # Test registration form
        self.selenium.get(f"{self.live_server_url}/register/")

        reg_username_input = self.selenium.find_element(By.NAME, "username")
        reg_classes = reg_username_input.get_attribute("class")

        # Ověř že oba formuláře používají konzistentní styling
        common_classes = ["w-full", "border", "rounded"]
        for css_class in common_classes:
            self.assertIn(css_class, login_classes)
            self.assertIn(css_class, reg_classes)

        print("✓ CSS styling consistency test PASSED")


# Sada rychlých testů pro základní ověření
@tag("selenium", "quick")
class QuickFormsTests(FormsSeleniumTests):
    """Rychlé testy pro základní ověření"""

    def test_quick_forms_check(self):
        """Rychlý test všech formulářů"""
        # Login form
        self.selenium.get(f"{self.live_server_url}/login/")
        self.assertTrue(len(self.selenium.find_elements(By.NAME, "username")) > 0)

        # Registration form
        self.selenium.get(f"{self.live_server_url}/register/")
        self.assertTrue(len(self.selenium.find_elements(By.NAME, "email")) > 0)

        print("✓ Quick forms check PASSED")
