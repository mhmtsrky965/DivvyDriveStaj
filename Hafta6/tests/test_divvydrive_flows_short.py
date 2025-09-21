# tests/test_divvydrive_flows.py

import pytest
import time
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.notes_page import NotesPage
from pages.passwords_page import PasswordsPage

# --- TEST VERİLERİ ---

USERNAME = "demo1"
PASSWORD = "123456Abc."

MAIN_FOLDER_NAME = f"mhmtsrkyodev6"  # Zaten mevcut olan klasör
RENAMED_MAIN_FOLDER = f"mhmtodev6srky"
RENAMED_SECOND_DOCX_NAME = f"odev666.docx"  # Zaten mevcut olan dosya

USER_TO_SHARE_WITH = "demo2"

NOTE_TITLE = f"mhmtsrky Notu"
NOTE_CONTENT = "notnotnotnotnot"

PASSWORD_SITE_NAME = f"mhmtsrky"
PASSWORD_URL = "https://test.divvydrive.com"
PASSWORD_USERNAME = "demo1"
PASSWORD_PASSWORD = "123456Abc."
PASSWORD_DESCRIPTION = "Selenium şifre kaydı"


def test_full_divvydrive_workflow(driver):
    """
    Linkle paylaşım adımından başlayan kısaltılmış test senaryosu.
    """
    print("\n--- KISALTILMIŞ TEST BAŞLADI (Linkle Paylaşımdan İtibaren) ---")

    # ADIM 1: Login Olma
    login_page = LoginPage(driver)
    dashboard_page = login_page.login(USERNAME, PASSWORD)
    print("ADIM 1: Başarıyla giriş yapıldı.")


    # ADIM 6: Notlar
    print("ADIM 6: Yeni not oluşturuluyor...")
    notes_page = dashboard_page.go_to_notes()
    time.sleep(2)

    # ADIM 7: Şifreler
    print("ADIM 4: Yeni şifre kaydı oluşturuluyor...")

    passwords_page = dashboard_page.go_to_passwords()
    time.sleep(2)

    passwords_page.create_new_password(
        name=PASSWORD_SITE_NAME,
        url=PASSWORD_URL,
        username=PASSWORD_USERNAME,  # PASSWORD_USER değil
        password=PASSWORD_PASSWORD,  # PASSWORD_PASS değil
        description=PASSWORD_DESCRIPTION
    )

    assert passwords_page.is_password_visible(PASSWORD_SITE_NAME), "HATA: Oluşturulan şifre listede bulunamadı!"
    print(" -> Yeni şifre oluşturuldu.")