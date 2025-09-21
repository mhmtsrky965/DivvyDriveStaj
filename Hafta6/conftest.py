# conftest.py

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    # WebDriverManager ile ChromeDriver'ı otomatik olarak kur ve başlat
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get("https://test.divvydrive.com/")

    # driver nesnesini teste gönder
    yield driver

    # Test bittikten sonra bu kısım çalışır
    print("\nTest bitti, tarayıcı kapatılıyor.")
    driver.quit()