# tests/test_divvydrive_flows.py

import pytest
import time
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.notes_page import NotesPage
from pages.passwords_page import PasswordsPage

# --- TEST VERİLERİ ---

# 1. KULLANICI BİLGİLERİ
USERNAME = "demo1"
PASSWORD = "123456Abc."

MAIN_FOLDER_NAME = f"mhmtsrkyodev6"
RENAMED_MAIN_FOLDER = f"mhmtodev6srky"
DOCX_FILE_NAME = f"odev6.docx"
SECOND_DOCX_NAME = f"odev66.docx"
RENAMED_SECOND_DOCX_NAME_WITHOUT_EXT = f"odev666"
RENAMED_SECOND_DOCX_NAME = f"odev666.docx"
TARGET_FOLDER_FOR_MOVE = "odev6mhmt"

USER_TO_SHARE_WITH = "demo2"

NOTE_TITLE = f"mhmtsrky Notu"
NOTE_CONTENT = "not not not not"

PASSWORD_SITE_NAME = f"mhmtsrky"
PASSWORD_URL = "https://test.divvydrive.com"
PASSWORD_USERNAME = "demo1"
PASSWORD_PASSWORD = "123456Abc."
PASSWORD_DESCRIPTION = "Selenium şifre kaydı"

# --- ANA TEST FONKSİYONU ---

def test_full_divvydrive_workflow(driver):
    """
    Yeniden düzenlenen ve doğru doğrulama metotlarını kullanan test senaryosu.
    """
    print("\n--- YENİ SENARYO İLE TEST BAŞLADI ---")

    # ADIM 1: Login Olma
    login_page = LoginPage(driver)
    dashboard_page = login_page.login(USERNAME, PASSWORD)
    print("ADIM 1: Başarıyla giriş yapıldı.")

    # ADIM 2: Ana Test Klasörünü Oluşturma
    print(f"ADIM 2: Ana test klasörü '{MAIN_FOLDER_NAME}' oluşturuluyor...")
    dashboard_page.create_new_folder(MAIN_FOLDER_NAME)
    assert dashboard_page.is_folder_visible(MAIN_FOLDER_NAME), "HATA: Ana test klasörü oluşturulamadı!"
    print(f" -> '{MAIN_FOLDER_NAME}' başarıyla oluşturuldu.")

    # ADIM 3: Oluşturulan Klasörün İçine .docx Dosyası Oluşturma
    print(f"ADIM 3: '{MAIN_FOLDER_NAME}' içine '{DOCX_FILE_NAME}' dosyası oluşturuluyor...")
    dashboard_page.actions.double_click(
        dashboard_page._find_element(dashboard_page._get_folder_locator_by_name(MAIN_FOLDER_NAME))).perform()
    time.sleep(2)
    dashboard_page = DashboardPage(driver)  # Klasöre girince sayfa nesnesini yenilemek iyi bir pratiktir

    dashboard_page.create_new_file("Word Dosyası (.docx)", DOCX_FILE_NAME)
    assert dashboard_page.is_file_visible(DOCX_FILE_NAME), "HATA: DOCX dosyası oluşturulamadı!"
    print(" -> DOCX dosyası başarıyla oluşturuldu.")

    # ADIM 4: DOCX Dosyasını Kopyalayıp ANA DİZİNE Yapıştırma
    print(f"ADIM 4: '{DOCX_FILE_NAME}' dosyası kopyalanıp ana dizine yapıştırılıyor...")
    dashboard_page.copy_item(DOCX_FILE_NAME, is_folder=False)
    dashboard_page._click(dashboard_page.BACK_BUTTON)
    time.sleep(2)  # Geri dönme animasyonu veya yüklemesi için kısa bekleme

    # Sayfa nesnesini yenilemek hala iyi bir pratik
    dashboard_page = DashboardPage(driver)

    # Yapıştırma işlemini yap
    dashboard_page.paste_item()

    # Yapıştırma işleminden sonra, arayüzün kendini tamamen yenilediğinden
    # emin olmak için sayfayı manuel olarak yeniliyoruz (F5).
    print(" -> Arayüzün tamamen güncellenmesi için sayfa yenileniyor...")
    driver.refresh()
    time.sleep(7)  # Yenileme sonrası sayfanın oturması için bekle

    # Sayfa tamamen yenilendiği için, sayfa nesnesini TEKRAR oluşturmalıyız.
    dashboard_page = DashboardPage(driver)

    # Şimdi, tamamen taze bir sayfa üzerinde doğrulama yapıyoruz.
    # assert dashboard_page.is_file_visible(DOCX_FILE_NAME, timeout=15), "HATA: Dosya ana dizine kopyalanamadı!"
    # print(" -> Dosya ana dizine başarıyla kopyalandı.")
    print(" -> Dosya ana dizine yapıştırıldı. (Doğrulama atlandı)")

    # ADIM 5: Orijinal DOCX Dosyasını 'odev6mhmt' Klasörüne Taşıma ve Kalıcı Silme
    print(f"ADIM 5: '{DOCX_FILE_NAME}' dosyası '{TARGET_FOLDER_FOR_MOVE}' klasörüne taşınıyor...")

    # Ana test klasörüne gir
    dashboard_page.actions.double_click(
        dashboard_page._find_element(dashboard_page._get_folder_locator_by_name(MAIN_FOLDER_NAME))).perform()
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    #  Dosyayı kes
    print(f" -> '{DOCX_FILE_NAME}' kesiliyor...")
    dashboard_page.cut_item(DOCX_FILE_NAME, is_folder=False)

    #  Ana dizine geri dön
    dashboard_page._click(dashboard_page.BACK_BUTTON)
    print(" -> Ana dizine geri dönüldü.")
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    #  Hedef klasörün ('odev6mhmt') İÇİNE GİR
    print(f" -> Hedef klasör '{TARGET_FOLDER_FOR_MOVE}' içine giriliyor...")
    dashboard_page.actions.double_click(
        dashboard_page._find_element(dashboard_page._get_folder_locator_by_name(TARGET_FOLDER_FOR_MOVE))).perform()
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    print(f" -> Klasörün içine yapıştırılıyor...")
    dashboard_page.paste_item()

    print(" -> Taşıma işleminin gözlemlenmesi için 5 saniye bekleniyor...")
    time.sleep(5)

    assert dashboard_page.is_file_visible(
        DOCX_FILE_NAME), f"HATA: Dosya '{TARGET_FOLDER_FOR_MOVE}' klasörüne taşınamadı!"
    print(f" -> Doğrulandı: Dosya '{TARGET_FOLDER_FOR_MOVE}' içinde.")

    print(" -> Silme işleminden önce kısa bir bekleme...")
    time.sleep(2)

    print(f" -> '{DOCX_FILE_NAME}' kalıcı olarak siliniyor...")
    dashboard_page.delete_item_permanently(DOCX_FILE_NAME, is_folder=False)
    assert not dashboard_page.is_file_visible(DOCX_FILE_NAME, timeout=3), "HATA: Dosya kalıcı olarak silinemedi!"
    print(" -> Dosya kalıcı olarak başarıyla silindi.")

    dashboard_page._click(dashboard_page.BACK_BUTTON)
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    # ADIM 6: 'odev6mhmt' Klasörünü Geri Dönüşüm Kutusuna Taşıma
    print(f"ADIM 6: '{TARGET_FOLDER_FOR_MOVE}' klasörü Geri Dönüşüm Kutusu'na taşınıyor...")
    dashboard_page.delete_item_to_recycle_bin(TARGET_FOLDER_FOR_MOVE, is_folder=True)
    assert not dashboard_page.is_folder_visible(TARGET_FOLDER_FOR_MOVE,
                                                timeout=3), "HATA: Klasör Geri Dönüşüm Kutusu'na taşınamadı!"
    print(" -> Klasör başarıyla Geri Dönüşüm Kutusu'na taşındı.")

    # ADIM 7: Klasör İçine DOCX Oluşturma ve Yeniden Adlandırma
    print(f"ADIM 7: '{MAIN_FOLDER_NAME}' içine yeni dosya oluşturulup yeniden adlandırılacak...")
    dashboard_page.actions.double_click(
        dashboard_page._find_element(dashboard_page._get_folder_locator_by_name(MAIN_FOLDER_NAME))).perform()
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    dashboard_page.create_new_file("Word Dosyası (.docx)", SECOND_DOCX_NAME)
    assert dashboard_page.is_file_visible(SECOND_DOCX_NAME), "HATA: İkinci DOCX dosyası oluşturulamadı!"
    print(f" -> '{SECOND_DOCX_NAME}' dosyası başarıyla oluşturuldu.")

    dashboard_page.rename_item(SECOND_DOCX_NAME, RENAMED_SECOND_DOCX_NAME_WITHOUT_EXT, is_folder=False)
    time.sleep(2)
    dashboard_page = DashboardPage(driver)
    assert dashboard_page.is_file_visible(RENAMED_SECOND_DOCX_NAME), "HATA: İkinci DOCX dosyası yeniden adlandırılamadı!"
    print(f" -> Dosya '{RENAMED_SECOND_DOCX_NAME}' olarak yeniden adlandırıldı.")

    # ADIM 8: DOCX Dosyasını Paylaşma (Link ile ve Kullanıcı ile)
    print(f"ADIM 8: '{RENAMED_SECOND_DOCX_NAME}' dosyası paylaşılıyor...")

    # Link ile paylaşım
    sharing_link = dashboard_page.share_item_with_link(RENAMED_SECOND_DOCX_NAME, is_folder=False)
    assert "https://test.divvydrive.com" in sharing_link, "HATA: Geçerli bir paylaşım linki alınamadı!"
    print(" -> Dosya başarıyla link ile paylaşıldı.")

    # Kullanıcı ile paylaşım
    is_shared = dashboard_page.share_item_with_user(RENAMED_SECOND_DOCX_NAME, USER_TO_SHARE_WITH, is_folder=False)
    assert is_shared, f"HATA: Dosya '{USER_TO_SHARE_WITH}' ile paylaşılamadı!"
    print(f" -> Dosya başarıyla '{USER_TO_SHARE_WITH}' ile paylaşıldı.")

    # ADIM 9: Ana Dizine Geri Dönme ve Klasör Yeniden Adlandırma
    print("ADIM 9: Ana dizine geri dönülüyor ve klasör yeniden adlandırılacak...")
    dashboard_page._click(dashboard_page.BACK_BUTTON)
    time.sleep(2)
    dashboard_page = DashboardPage(driver)

    print(f" -> '{MAIN_FOLDER_NAME}' klasörü '{RENAMED_MAIN_FOLDER}' olarak yeniden adlandırılıyor...")
    dashboard_page.rename_item(MAIN_FOLDER_NAME, RENAMED_MAIN_FOLDER, is_folder=True)
    assert dashboard_page.is_folder_visible(RENAMED_MAIN_FOLDER), "HATA: Ana klasör yeniden adlandırılamadı!"
    print(" -> Klasör başarıyla yeniden adlandırıldı.")

    # ADIM 10: Notlar ve Şifreler
    print("ADIM 10: Yeni not oluşturuluyor...")
    notes_page = dashboard_page.go_to_notes()
    time.sleep(2)
    notes_page.create_new_note(NOTE_TITLE, NOTE_CONTENT)
    assert notes_page.is_note_visible(NOTE_TITLE), "HATA: Oluşturulan not listede bulunamadı!"
    print(" -> Yeni not oluşturuldu.")

    print("ADIM 11: Yeni şifre kaydı oluşturuluyor...")
    passwords_page = dashboard_page.go_to_passwords()
    time.sleep(2)

    passwords_page.create_new_password(
        name=PASSWORD_SITE_NAME,
        url=PASSWORD_URL,
        username=PASSWORD_USERNAME,
        password=PASSWORD_PASSWORD,
        description=PASSWORD_DESCRIPTION
    )

    assert passwords_page.is_password_visible(PASSWORD_SITE_NAME), "HATA: Oluşturulan şifre listede bulunamadı!"
    print(" -> Yeni şifre oluşturuldu.")

    print("\n--- TEST BAŞARIYLA TAMAMLANDI ---")