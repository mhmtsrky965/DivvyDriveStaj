# pages/login_page.py

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage

class LoginPage(BasePage):
    # --- Locators ---
    USERNAME_INPUT = (By.ID, "kullaniciAdi")
    PASSWORD_INPUT = (By.ID, "sifre")
    LOGIN_BUTTON = (By.ID, "oturumAcButton")

    def __init__(self, driver):
        super().__init__(driver)

    def login(self, username, password):
        self._send_keys(self.USERNAME_INPUT, username)
        self._send_keys(self.PASSWORD_INPUT, password)
        self._click(self.LOGIN_BUTTON)
        # Login sonrası DashboardPage'e geçileceği için o sınıfı döndürüyoruz
        return DashboardPage(self.driver)