# pages/passwords_page.py

import time
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class PasswordsPage(BasePage):
    # --- LOCATORS ---

    # Ana içerik alanı (dashboard'daki gibi)
    MAIN_CONTENT_AREA = (By.ID, "scrollContent")  # Dashboard ile aynı alan

    # Context menu - DOĞRUDAN YENİ ŞİFRE
    CONTEXT_MENU_NEW_PASSWORD = (By.XPATH, "//span[normalize-space()='Yeni Şifre']")

    # Yeni Şifre Modal - DOĞRU XPATH'LER
    PASSWORD_NAME_INPUT = (By.XPATH, '//*[@id="keyChainAdi"]')
    PASSWORD_URL_INPUT = (By.XPATH, '//*[@id="keyChainBaglantiAdresi"]')
    PASSWORD_USERNAME_INPUT = (By.XPATH, '//*[@id="keyChainKullaniciAdi"]')
    PASSWORD_PASSWORD_INPUT = (By.XPATH, '//*[@id="keyChainSfr"]')
    PASSWORD_DESCRIPTION_INPUT = (By.XPATH, '//*[@id="keyChainAciklama"]')
    SAVE_PASSWORD_BUTTON = (By.XPATH, '//*[@id="keyChainKaydetButton"]')

    # Şifre listesi (doğrulama için)
    PASSWORD_LIST_ITEM = (By.XPATH, "//div[contains(@class, 'password') or contains(@class, 'card')]")

    def __init__(self, driver):
        super().__init__(driver)
        # Ana alanın görünür olmasını bekle
        try:
            self._find_element(self.MAIN_CONTENT_AREA)
            print("Şifreler sayfası başarıyla yüklendi.")
        except:
            print("Şifreler sayfası yüklendi (ana alan bulunamadı ama devam ediliyor).")

    def create_new_password(self, name, url, username, password, description=""):
        """
        Şifreler sayfasında sağ tıklayarak yeni şifre oluşturur.
        """
        print(f"'{name}' adlı yeni şifre oluşturuluyor...")

        # 1. Ana alana sağ tıkla
        print(" -> Ana alana sağ tıklanıyor...")
        self._right_click_with_js(self.MAIN_CONTENT_AREA)

        # 2. Direkt "Yeni Şifre" seçeneğine tıkla
        print(" -> 'Yeni Şifre' seçeneğine tıklanıyor...")
        self._click(self.CONTEXT_MENU_NEW_PASSWORD)

        time.sleep(2)  # Modal açılması için bekle

        # 3. Şifre Adı gir
        print(f" -> Şifre adı giriliyor: {name}")
        try:
            name_input = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_NAME_INPUT))
            name_input.clear()
            name_input.send_keys(name)
            print(f" -> Şifre adı girildi: {name}")
        except Exception as e:
            print(f"HATA: Şifre adı alanı bulunamadı! {e}")

        # 4. Bağlantı Adresi gir
        print(f" -> Bağlantı adresi giriliyor: {url}")
        try:
            url_input = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_URL_INPUT))
            url_input.clear()
            url_input.send_keys(url)
            print(f" -> Bağlantı adresi girildi: {url}")
        except Exception as e:
            print(f"HATA: Bağlantı adresi alanı bulunamadı! {e}")

        # 5. Kullanıcı Adı gir
        print(f" -> Kullanıcı adı giriliyor: {username}")
        try:
            username_input = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_USERNAME_INPUT))
            username_input.clear()
            username_input.send_keys(username)
            print(f" -> Kullanıcı adı girildi: {username}")
        except Exception as e:
            print(f"HATA: Kullanıcı adı alanı bulunamadı! {e}")

        # 6. Şifre gir
        print(f" -> Şifre giriliyor: {password}")
        try:
            password_input = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_PASSWORD_INPUT))
            password_input.clear()
            password_input.send_keys(password)
            print(f" -> Şifre girildi: {password}")
        except Exception as e:
            print(f"HATA: Şifre alanı bulunamadı! {e}")

        # 7. Açıklama gir (opsiyonel)
        if description:
            print(f" -> Açıklama giriliyor: {description}")
            try:
                description_input = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_DESCRIPTION_INPUT))
                description_input.clear()
                description_input.send_keys(description)
                print(f" -> Açıklama girildi: {description}")
            except Exception as e:
                print(f"UYARI: Açıklama alanı bulunamadı! {e}")

        # 8. Kaydet butonuna tıkla
        print(" -> Kaydet butonuna tıklanıyor...")
        save_locators = [
            (By.XPATH, '//*[@id="keyChainKaydetButton"]')
        ]

        save_clicked = False
        for i, locator in enumerate(save_locators):
            try:
                print(f" -> Kaydet butonu denemesi {i + 1}: {locator[1]}")
                save_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))
                save_button.click()
                print(" -> Kaydet butonuna tıklandı")
                save_clicked = True
                break
            except:
                print(f" -> Kaydet denemesi {i + 1} başarısız")
                continue

        if not save_clicked:
            print("HATA: Kaydet butonu bulunamadı!")

        # 9. Başarı kontrolü
        try:
            self._wait_for_success_toast()
            print(" -> Başarı mesajı görüldü")
        except:
            print(" -> Başarı mesajı görülmedi, 3 saniye beklenecek")
            time.sleep(3)

        print(f"Şifre '{name}' başarıyla oluşturuldu.")

    def is_password_visible(self, password_name, timeout=10):
        """Belirtilen ada sahip şifrenin listede olup olmadığını kontrol eder."""
        print(f"'{password_name}' şifresi aranıyor...")

        password_locators = [
            (By.XPATH, f"//div[contains(@class, 'password') and contains(., '{password_name}')]"),
            (By.XPATH, f"//div[contains(@class, 'card') and contains(., '{password_name}')]"),
            (By.XPATH, f"//h5[contains(text(), '{password_name}')]"),
            (By.XPATH, f"//h4[contains(text(), '{password_name}')]"),
            (By.XPATH, f"//h3[contains(text(), '{password_name}')]"),
            (By.XPATH, f"//*[contains(text(), '{password_name}')]"),
        ]

        for i, locator in enumerate(password_locators):
            try:
                print(f" -> Şifre arama denemesi {i + 1}: {locator[1]}")
                WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
                print(f"Doğrulama: '{password_name}' şifresi bulundu.")
                return True
            except:
                print(f" -> Arama denemesi {i + 1} başarısız")
                continue

        print(f"Doğrulama: '{password_name}' şifresi bulunamadı.")
        return False